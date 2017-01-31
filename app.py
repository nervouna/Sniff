import string
import random
from functools import wraps

import requests
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import flash
from flask import url_for
from flask import abort

from leancloud import User
from leancloud import Object
from leancloud import GeoPoint
from leancloud import LeanCloudError
from geolite2 import geolite2


app = Flask(__name__)


Visits = Object.extend('Visits')
Shortened = Object.extend('Shortened')
URL_KEY_SIZE = 4


class Sniffer(User):
    pass


def login_required(func):
    @wraps(func)
    def secret_view(*args, **kwargs):
        return func(*args, **kwargs)
    return secret_view


@app.route('/login')
def login_form():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username, password = request.form['username'], request.form['password']
    sniffer = Sniffer()
    try:
        sniffer.login(username, password)
        flash('logged in', 'success')
        return redirect(url_for('index'))
    except LeanCloudError as e:
        flash(e.error, 'danger')
        return redirect(url_for('login_form'))


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
@login_required
def shorten():
    lurl = request.form['url']
    surl = None
    try:
        assert url_is_dead(lurl)
        flash('Given URL is dead.', 'danger')
    except (requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema) as e:
        flash('Please enter an URL with valid schema. e.g: http://, https://.', 'danger')
    except AssertionError:
        url_key = gen_short_url(lurl)
        surl = request.url_root + url_key
    finally:
        return render_template('index.html', surl=surl)


@app.route('/<surl>')
def go(surl):
    long_url = get_long(surl)
    if long_url is None:
        abort(404)
    visit = Visits()
    visit.set('target', long_url)
    ip_address = request.headers.get('x-real-ip')
    if ip_address:
        geo_info = get_geo_info(ip_address)
        visit.set(geo_info)
    visit.set('ip_address', ip_address)
    browser_info = {
        'browser': 'weixin' if 'MicroMessenger' in request.user_agent.string else request.user_agent.browser,
        'browser_version': request.user_agent.version,
        'platform': request.user_agent.platform,
        'language': request.user_agent.language
    }
    visit.set(browser_info)
    campaign_info = {
        'campaign': request.args.get('utm_campaign'),
        'campaign_source': request.args.get('utm_source'),
        'campaign_medium': request.args.get('utm_medium'),
        'campaign_term': request.args.get('utm_term'),
        'campaign_content': request.args.get('utm_content')
    }
    visit.set(campaign_info)
    visit.save()
    return redirect(get_long(surl).get('long'))


def url_is_dead(url: str) -> bool:
    """Check URL's availability.

    Args:
        url: The URL string to be checked.

    Returns:
        True for URL not available, False otherwise.
    """
    res = requests.head(url)
    if res.status_code >= 400:
        return True
    elif res.status_code < 400:
        return False


def gen_random_string(size: str) -> str:
    """Generates a random string of given length.

    Args:
        size: The length of the desired random string.

    Returns:
        random_string: A string constructed with random ascii letters and digits.
    """
    random_string = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(size))
    try:
        shortened_url = Shortened.query.equal_to('short', random_string).first()
        return gen_random_string(size + 1)
    except LeanCloudError as e:
        if e.code == 101:
            return random_string
        else:
            raise e


def get_short(lurl: str) -> Shortened:
    """Get the URL key for the given source URL if exists."""
    try:
        surl = Shortened.query.equal_to('long', lurl).first()
    except LeanCloudError as e:
        if e.code == 101:
            surl = None
        else:
            raise e
    return surl


def get_long(surl: str) -> Shortened:
    """Get the source URL for the given URL key if exists."""
    try:
        lurl = Shortened.query.equal_to('short', surl).first()
    except LeanCloudError as e:
        if e.code == 101:
            lurl = None
        else:
            raise e
    return lurl


def gen_short_url(lurl: str) -> str:
    """Generates the URL key for the given source URL.

    Args:
        lurl: The source URL to be shortened.

    Returns:
        surl: The shortened URL key.
    """
    if get_long(lurl) is not None:
        return lurl
    elif get_short(lurl) is not None:
        return get_short(lurl).get('short')
    else:
        shortened = Shortened()
        surl = gen_random_string(size=URL_KEY_SIZE)
        shortened.set({"long": lurl, "short": surl})
        shortened.save()
        return surl


def get_geo_info(ip: str) -> dict:
    """Generates a dictionary contains user's geo info.

    Args:
        ip: IP address.

    Returns:
        geo_info: User's geo location.
    """
    reader = geolite2.reader()
    raw_info = reader.get(ip)
    geo_info = {}
    geo_info['continent'] = raw_info['continent']['names']['en']
    geo_info['country'] = raw_info['country']['names']['en']
    geo_info['subdivisions'] = [x['names']['en'] for x in raw_info['subdivisions']],
    geo_info['city'] = raw_info['city']['names']['en']
    geo_info['location'] = GeoPoint(raw_info['location']['latitude'], raw_info['location']['longitude'])
    return geo_info
