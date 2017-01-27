# coding: utf-8

import requests
import string
import random

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import flash
from flask import url_for

from leancloud import Object
from leancloud import LeanCloudError


URL_KEY_SIZE = 4

app = Flask(__name__)


Visits = Object.extend('Visits')
Shortened = Object.extend('Shortened')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def shorten():
    lurl = request.form['url']
    if url_is_dead(lurl):
        flash('Given URL is dead.', 'error')
        return render_template('index.html')
    else:
        surl = gen_short_url(lurl)
        return render_template('index.html', surl=request.url_root + surl)


@app.route('/<surl>')
def go(surl):
    long_url = get_long(surl)
    visit = Visits()
    visit.set('target', long_url)
    if not app.debug:
        visit.set('ip_address', request.headers.get('x-real-ip'))
    else:
        visit.set('ip_address', request.remote_addr)
    visit.set('browser', request.user_agent.browser)
    visit.set('platform', request.user_agent.platform)
    visit.set('user_agent_string', request.user_agent.string)
    visit.save()
    return redirect(get_long(surl).get('long'))


def url_is_dead(url):
    res = requests.head(url)
    if res.status_code >= 400:
        return True
    elif res.status_code < 400:
        return False


def gen_random_string(size):
    random_string = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(size))
    try:
        shortened_url = Object.extend('Shortened').query.equal_to('short', random_string).first()
        return gen_random_string(size + 1)
    except LeanCloudError as e:
        if e.code == 101:
            return random_string
        else:
            raise e


def get_short(lurl):
    surl = Object.extend('Shortened').query.equal_to('long', lurl).first()
    return surl


def get_long(surl):
    lurl = Object.extend('Shortened').query.equal_to('short', surl).first()
    return lurl


def gen_short_url(lurl):
    '''Generates shortened URL from given long url, returns a string as the
    shortened url's key.
    '''
    try:
        if get_long(lurl) is not None:
            return lurl
    except LeanCloudError as e:
        if e.code == 101:
            pass
        else:
            raise e
    try:
        return get_short(lurl).get('short')
    except LeanCloudError as e:
        if e.code == 101:
            pass
        else:
            raise e
    shortened = Shortened()
    # Hard coded size. Fix later ( or never )
    size = URL_KEY_SIZE
    surl = gen_random_string(size=size)
    shortened.set('long', lurl)
    shortened.set('short', surl)
    shortened.save()
    return surl
