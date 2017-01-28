# Campaign Tracker on LeanCloud

CTL is a marketing campaign tracker. It checks the availability of the given URL, shortens it, and tracks who / when / where / how the link is clicked.

## Features

* Checks if the URL is alive
* Shortens the URL
* Logs who / when / where / how the link is clicked

## Requirements

USL runs on Python 3. It requires [flask][1], [requests][2] and [LeanCloud Python SDK][3].

## Quick Start

### Before You Begin

USL is a [LeanCloud][4] app. Before getting the code up and running, there're some chores to do.

1. Create an app on [LeanCloud dashboard][5], and set a domain name for the app.
2. Set environment variable `FLASK_SECRET_KEY` in the LeanCloud dashboard. Refer to [this][6] on how to make a good solid secret key.
3. Install [LeanCloud CLI][7]. It's not required, but is highly recommended.

### Deploy Methods

Clone this repo, type `lean login` then `lean checkout` to link your local repo to the LeanCloud app you've just created.

Use [virtualenv][8] to create a virtual environment for this app. Activate the virtual environment, then use `pip` to install the requirements.

Use `lean deploy` to deploy the code onto the cloud. After that, visit the site with the domain name you set before.

In short:

```bash
$ git clone https://github.com/nervouna/URL-Shortener.git
$ cd URL-Shortener
$ virtualenv venv --python=python3
$ source venv/bin/activate
$ pip install -r requirements.txt
$ lean login
$ lean checkout
$ lean deploy
```

### Where's the Data?

Check out the data in the [LeanCloud dashboard][5]. All the URLs are stored in the `Shortened` class, and the visitor footprints are stored in the `Visits` class.

### Debugging

You can always use `lean up` to fire up a debuggable instance on your machine, and visit it via `http://127.0.0.1:3000` by default.

## Miscellaneous

### Todos

* [ ] QRCode for short links
* [ ] Export data in CSV
* [ ] Browser plugins

### Maybes

* 🤔 Full-functioning dashboard

### License

License: [WTFPL][9]

Author: GUAN Xiaoyu ([guanxy@me.com][10])



[1]: http://flask.pocoo.org
[2]: https://github.com/kennethreitz/requests
[3]: https://github.com/leancloud/python-sdk
[4]: https://leancloud.cn/
[5]: https://leancloud.cn/dashboard/applist.html#/apps
[6]: https://gist.github.com/nervouna/cd58fb09c22826eaaff996793de72d85
[7]: https://github.com/leancloud/lean-cli/releases/latest
[8]: https://github.com/pypa/virtualenv
[9]: https://github.com/nervouna/URL-Shortener/blob/master/LICENSE
[10]: mailto:guanxy@me.com
