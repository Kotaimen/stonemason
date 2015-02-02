# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '2/2/15'

"""Stonemason Tile Server CLI"""

import click

from stonemason.service.tileserver import TileServerApp


@click.command()
@click.option('--debug/--no-debug', default=False)
@click.option('--bind', default='localhost:7086')
def tileserver(debug, bind):
    app = TileServerApp()
    host, port = bind.split(':')
    app.run(debug=debug, host=host, port=int(port))


if __name__ == '__main__':
    tileserver()
