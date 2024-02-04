#!/usr/bin/python3
'''Defines views for managing places within the API.'''
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest

from api.v1.views import app_views
from models import storage
from models.place import Place
from models.state import State
from models.amenity import Amenity
from models.city import City
from models.user import User


@app_views.route('/cities/<city_id>/places', methods=['GET', 'POST'])
@app_views.route('/places/<place_id>', methods=['GET', 'DELETE', 'PUT'])
def handle_places(city_id=None, place_id=None):
    '''Handles requests to the places endpoint.'''
    handlers = {
        'GET': get_places,
        'DELETE': remove_place,
        'POST': add_place,
        'PUT': update_place
    }
    if request.method in handlers:
        return handlers[request.method](city_id, place_id)
    else:
        raise MethodNotAllowed(list(handlers.keys()))


def get_places(city_id=None, place_id=None):
    '''Retrieves places by ID or all places in a given city.'''
    if city_id:
        city = storage.get(City, city_id)
        if city:
            all_places = city.places
            places_data = [place.to_dict() for place in all_places]
            return jsonify(places_data)
    elif place_id:
        place = storage.get(Place, place_id)
        if place:
            return jsonify(place.to_dict())
    raise NotFound()


def remove_place(city_id=None, place_id=None):
    '''Deletes a place by ID.'''
    if place_id:
        place = storage.get(Place, place_id)
        if place:
            storage.delete(place)
            storage.save()
            return jsonify({}), 200
    raise NotFound()


def add_place(city_id=None, place_id=None):
    '''Adds a new place.'''
    city = storage.get(City, city_id)
    if not city:
        raise NotFound()
    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Data must be in JSON format')
    if 'user_id' not in data:
        raise BadRequest(description='User ID is missing')
    user = storage.get(User, data['user_id'])
    if not user:
        raise NotFound()
    if 'name' not in data:
        raise BadRequest(description='Name is missing')
    data['city_id'] = city_id
    new_place = Place(**data)
    new_place.save()
    return jsonify(new_place.to_dict()), 201


def update_place(city_id=None, place_id=None):
    '''Updates a place by ID.'''
    reserved_keys = ('id', 'user_id', 'city_id', 'created_at', 'updated_at')
    place = storage.get(Place, place_id)
    if place:
        data = request.get_json()
        if type(data) is not dict:
            raise BadRequest(description='Data must be in JSON format')
        for key, value in data.items():
            if key not in reserved_keys:
                setattr(place, key, value)
        place.save()
        return jsonify(place.to_dict()), 200
    raise NotFound()


@app_views.route('/places_search', methods=['POST'])
def find_places():
    '''Finds places based on a list of State, City, or Amenity IDs.'''
    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Data must be in JSON format')

    places = get_filtered_places(data)
    return jsonify(places)


def get_filtered_places(data):
    '''Filters places based on State, City, and Amenity IDs.'''
    state_ids = data.get('states', [])
    city_ids = data.get('cities', [])
    amenity_ids = data.get('amenities', [])

    if not any([state_ids, city_ids]):
        all_places = storage.all(Place).values()
    else:
        all_places = []

        for state_id in state_ids:
            state = storage.get(State, state_id)
            if state:
                all_places.extend(state.places)

        for city_id in city_ids:
            city = storage.get(City, city_id)
            if city:
                all_places.extend(city.places)

    if amenity_ids:
        all_places = filter_places_by_amenities(all_places, amenity_ids)

    return sanitize_places_data(all_places)


def filter_places_by_amenities(places, amenity_ids):
    '''Filters places by Amenity IDs.'''
    filtered_places = []
    for place in places:
        if all(amenity_id in [amenity.id for amenity in place.amenities]
               for amenity_id in amenity_ids):
            filtered_places.append(place)
    return filtered_places


def sanitize_places_data(places):
    '''Removes sensitive data from places.'''
    sanitized_places = []
    for place in places:
        place_data = place.to_dict()
        place_data.pop('amenities', None)
        sanitized_places.append(place_data)
    return sanitized_places
