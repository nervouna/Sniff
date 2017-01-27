import string
import random
from json import loads

import requests
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import flash
from flask import url_for
from flask import abort

from leancloud import Object
from leancloud import GeoPoint
from leancloud import LeanCloudError
from geolite2 import geolite2


app = Flask(__name__)


Visits = Object.extend('Visits')
Shortened = Object.extend('Shortened')
URL_KEY_SIZE = 4


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
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
    ip_address = request.headers.get('x-real-ip')
    geo_info = None if ip_address is None else get_geo_info(ip_address)
    visit.set({
        'target': long_url,
        'ip_address': ip_address,
        'browser': request.user_agent.browser,
        'browser_version': request.user_agent.version,
        'platform': request.user_agent.platform,
        'language': request.user_agent.language,
        'continent': geo_info['continent']['names']['en'],
        'country': geo_info['country']['names']['en'],
        'subdivisions': [x['names']['en'] for x in geo_info['subdivisions']],
        'city': geo_info['city']['names']['en'],
        'location': GeoPoint(geo_info['location']['latitude'], geo_info['location']['longitude'])
    })
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


def get_geo_info(ip: str) -> str:
    reader = geolite2.reader()
    geo_info = reader.get(ip)
    return geo_info
