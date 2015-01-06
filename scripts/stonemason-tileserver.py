#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from stonemason.service.tileserver import AppBuilder

application = app = AppBuilder().build('settings.py')

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8080)
