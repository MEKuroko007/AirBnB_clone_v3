from flask import Flask, make_response, jsonify
from os import getenv
from api.v1.views import app_views
from models import storage
from flask_cors import CORS

app = Flask(__name__)
app.url_map.strict_slashes = False
app.register_blueprint(app_views)
cors = CORS(app, resources={r"/api/*": {"origins": "0.0.0.0"}})


@app.teardown_appcontext
def teardown_appcontext(exception):
    """Close db"""
    storage.close()


@app.errorhandler(404)
def not_found(error):
    """ 404 Error - Not Found"""
    return make_response(jsonify({'error': "Not found"}), 404)


if __name__ == "__main__":
    host = getenv('HBNB_API_HOST', '0.0.0.0')
    port = int(getenv('HBNB_API_PORT', 5000))
    app.run(host=host, port=port, threaded=True)
