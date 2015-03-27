# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash, session, g, jsonify

from sqlalchemy import desc

from apps import app, db

from apps.models import (User, Comment, Log, Group, Project)


@app.route("/")
def main():
    return "main"



#
# @error Handlers
#
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404


# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('error/500.html'), 500


