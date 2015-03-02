# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

from flask import Blueprint

from .views import AdminView


def create_blueprint(**kwargs):
    blueprint = Blueprint('admin', __name__, template_folder='templates')

    view = AdminView.as_view('admin', **kwargs)

    blueprint.add_url_rule(
        endpoint='overview',
        rule='/',
        view_func=view,
        methods=['GET']
    )

    return blueprint

