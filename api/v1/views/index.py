#!/usr/bin/python3
'''index for api.'''
from flask import jsonify

from api.v1.views import app_views
from models import storage



@app_views.route('/status')
def get_status():
    '''return status of api.'''
    return jsonify(status='OK')
