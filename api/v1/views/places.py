#!/usr/bin/python3
"""Handles RESTful API actions for Places."""
from flask import jsonify, abort, request, make_response
from api.v1.views import app_views
from models import storage
from models.city import City
from models.place import Place
from models.user import User


@app_views.route('/cities/<city_id>/places',
                 methods=['GET'], strict_slashes=False)
def get_places(city_id):
    """Retrieves all places of a city."""
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<place_id>',
                 methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """Retrieves a specific place."""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_place(place_id):
    """Deletes a place."""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places',
                 methods=['POST'], strict_slashes=False)
def create_place(city_id):
    """Creates a new place."""
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    if not request.json:
        abort(400, 'Request data must be in JSON format')
    required_fields = ['user_id', 'name']
    for field in required_fields:
        if field not in request.json:
            abort(400, f'Missing {field} field')
    user_id = request.json['user_id']
    user = storage.get(User, user_id)
    if not user:
        abort(404)
    new_place = Place(city_id=city_id, **request.json)
    storage.new(new_place)
    storage.save()
    return jsonify(new_place.to_dict()), 201


@app_views.route('/places/<place_id>',
                 methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    """Updates a place."""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    if not request.json:
        abort(400, 'Request data must be in JSON format')
    fields_to_update = ['name', 'description', 'number_rooms',
                        'number_bathrooms', 'max_guest', 'price_by_night',
                        'latitude', 'longitude']
    for field in fields_to_update:
        if field in request.json:
            setattr(place, field, request.json[field])
    storage.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places_search',
                 methods=['POST'], strict_slashes=False)
def places_search():
    """Searches for places based on given criteria."""
    if not request.json:
        abort(400, 'Request data must be in JSON format')
    data = request.json
    states = data.get('states', [])
    cities = data.get('cities', [])
    amenities = data.get('amenities', [])
    places = storage.all(Place).values()

    filtered_places = []
    for place in places:
        if (not states or place.city.state_id in states) and \
           (not cities or place.city_id in cities) and \
           (not amenities or all(amenity.id in place.
                                 amenities for amenity in amenities)):
            filtered_places.append(place.to_dict())
    return jsonify(filtered_places)
