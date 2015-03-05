# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

from flask import Blueprint

from .views import health_check


def create_blueprint(**kwargs):
    blueprint = Blueprint('health_check', __name__)

    blueprint.add_url_rule(
        endpoint='health_check',
        rule='/health_check',
        view_func=health_check,
        methods=['GET']
    )

    return blueprint
