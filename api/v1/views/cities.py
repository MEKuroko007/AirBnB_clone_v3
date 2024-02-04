#!/usr/bin/python3
"""Defines views for handling cities in the API."""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.city import City
from models.state import State


@app_views.route('/states/<state_id>/cities', methods=['GET'])
@app_views.route('/states/<state_id>/cities/', methods=['GET'])
def list_cities_of_state(state_id):
    """Retrieves a list of cities for a given state."""
    all_states = storage.all(State).values()
    state_obj = next((state for state in all_states if state.id == state_id), None)
    if not state_obj:
        abort(404)
    list_cities = [city.to_dict() for city in storage.all(City).values() if city.state_id == state_id]
    return jsonify(list_cities)


@app_views.route('/states/<state_id>/cities', methods=['POST'])
@app_views.route('/states/<state_id>/cities/', methods=['POST'])
def create_city(state_id):
    """Creates a new city."""
    if not request.json:
        abort(400, 'Not a JSON')
    if 'name' not in request.json:
        abort(400, 'Missing name')
    state_obj = storage.get(State, state_id)
    if not state_obj:
        abort(404)
    new_city = City(name=request.json['name'], state_id=state_id)
    storage.new(new_city)
    storage.save()
    return jsonify(new_city.to_dict()), 201


@app_views.route('/cities/<city_id>', methods=['GET'])
def get_city(city_id):
    """Retrieves a specific city."""
    city_obj = storage.get(City, city_id)
    if not city_obj:
        abort(404)
    return jsonify(city_obj.to_dict())


@app_views.route('/cities/<city_id>', methods=['DELETE'])
def delete_city(city_id):
    """Deletes a city."""
    city_obj = storage.get(City, city_id)
    if not city_obj:
        abort(404)
    storage.delete(city_obj)
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>', methods=['PUT'])
def update_city(city_id):
    """Updates a city."""
    city_obj = storage.get(City, city_id)
    if not city_obj:
        abort(404)
    if not request.json:
        abort(400, 'Not a JSON')
    if 'name' not in request.json:
        abort(400, 'Missing name')
    city_obj.name = request.json['name']
    storage.save()
    return jsonify(city_obj.to_dict()), 200
