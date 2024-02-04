#!/usr/bin/python3
"""app for flask api"""
from flask import Flask
from os import getenv
from api.v1.views import app_views
from models import storage
from flask import jsonify
from flask_cors import CORS

app = Flask(__name__)
'''The Flask web application.'''
app_host = getenv('HBNB_API_HOST', '0.0.0.0')
app_port = int(getenv('HBNB_API_PORT', '5000'))
app.url_map.strict_slashes = False
app.register_blueprint(app_views)
cors = CORS(app, resources={r"/api/*": {"origins": "0.0.0.0"}})


@app.teardown_appcontext
def teardown_appcontext(exception):
    """Close the session"""
    storage.close()


@app.errorhandler(404)
def error_404(error):
    '''Handles the 404 HTTP error code.'''
    return jsonify(error='Not found'), 404


if __name__ == "__main__":
    host = getenv('HBNB_API_HOST', '0.0.0.0')
    port = int(getenv('HBNB_API_PORT', 5000))
    app.run(host=host, port=port, threaded=True)
