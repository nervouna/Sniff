# -*- coding: utf-8 -*-

import os

import leancloud

from app import app


APP_ID = os.environ['LEANCLOUD_APP_ID']
APP_KEY = os.environ['LEANCLOUD_APP_KEY']
MASTER_KEY = os.environ['LEANCLOUD_APP_MASTER_KEY']
PORT = int(os.environ['LEANCLOUD_APP_PORT'])

leancloud.init(APP_ID, app_key=APP_KEY, master_key=MASTER_KEY)
# 如果需要使用 master key 权限访问 LeanCLoud 服务，请将这里设置为 True
leancloud.use_master_key(False)

application = app


if __name__ == '__main__':
    # 只在本地开发环境执行的代码
    from werkzeug.serving import run_simple
    app.debug = True
    run_simple('127.0.0.1', 3000, app, use_reloader=True, use_debugger=True)
