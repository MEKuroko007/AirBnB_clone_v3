#!/usr/bin/python3
'''Defines views for handling cities in the API.'''

from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest

from api.v1.views import app_views
from models import storage, storage_t
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State


@app_views.route('/states/<state_id>/cities', methods=['GET', 'POST'])
@app_views.route('/cities/<city_id>', methods=['GET', 'DELETE', 'PUT'])
def handle_cities(state_id=None, city_id=None):
    '''Route handler for cities.'''
    methods = {
        'GET': get_cities,
        'POST': add_city,
        'DELETE': delete_city,
        'PUT': update_city
    }

    if request.method in methods:
        return methods[request.method](state_id, city_id)
    else:
        raise MethodNotAllowed()


def get_cities(state_id=None, city_id=None):
    '''Retrieve cities by state or by city id.'''
    if state_id:
        state = storage.get(State, state_id)
        if state:
            cities = [city.to_dict() for city in state.cities]
            return jsonify(cities)
    elif city_id:
        city = storage.get(City, city_id)
        if city:
            return jsonify(city.to_dict())
    raise NotFound()


def delete_city(state_id=None, city_id=None):
    '''Delete a city by its id.'''
    if city_id:
        city = storage.get(City, city_id)
        if city:
            storage.delete(city)
            if storage_t != "db":
                for place in storage.all(Place).values():
                    if place.city_id == city_id:
                        for review in storage.all(Review).values():
                            if review.place_id == place.id:
                                storage.delete(review)
                        storage.delete(place)
            storage.save()
            return jsonify({}), 200
    raise NotFound()


def add_city(state_id=None, city_id=None):
    '''Add a new city.'''
    state = storage.get(State, state_id)
    if not state:
        raise NotFound()
        
    data = request.get_json()
    if not isinstance(data, dict):
        raise BadRequest(description='Invalid JSON')

    if 'name' not in data:
        raise BadRequest(description='Missing name')

    data['state_id'] = state_id
    city = City(**data)
    city.save()
    return jsonify(city.to_dict()), 201


def update_city(state_id=None, city_id=None):
    '''Update an existing city.'''
    xkeys = ('id', 'state_id', 'created_at', 'updated_at')
    if city_id:
        city = storage.get(City, city_id)
        if city:
            data = request.get_json()
            if not isinstance(data, dict):
                raise BadRequest(description='Invalid JSON')
                
            for key, value in data.items():
                if key not in xkeys:
                    setattr(city, key, value)

            city.save()
            return jsonify(city.to_dict()), 200
    raise NotFound()
