#!/usr/bin/python3
'''Defines views for managing amenities within the API.'''
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest

from api.v1.views import app_views
from models import storage
from models.amenity import Amenity


ALLOWED_METHODS = ['GET', 'DELETE', 'POST', 'PUT']
'''Accepted methods for the amenities endpoint.'''


@app_views.route('/amenities', methods=ALLOWED_METHODS)
@app_views.route('/amenities/<amenity_id>', methods=ALLOWED_METHODS)
def handle_amenities(amenity_id=None):
    '''Handles requests to the amenities endpoint.'''
    handlers = {
        'GET': get_amenities,
        'DELETE': remove_amenity,
        'POST': add_amenity,
        'PUT': update_amenity,
    }
    if request.method in handlers:
        return handlers[request.method](amenity_id)
    else:
        raise MethodNotAllowed(list(handlers.keys()))


def get_amenities(amenity_id=None):
    '''Retrieves amenity by ID or all amenities.'''
    all_amenities = storage.all(Amenity).values()
    if amenity_id:
        result = list(filter(lambda x: x.id == amenity_id, all_amenities))
        if result:
            return jsonify(result[0].to_dict())
        raise NotFound()
    all_amenities = list(map(lambda x: x.to_dict(), all_amenities))
    return jsonify(all_amenities)


def remove_amenity(amenity_id=None):
    '''Deletes an amenity by ID.'''
    all_amenities = storage.all(Amenity).values()
    result = list(filter(lambda x: x.id == amenity_id, all_amenities))
    if result:
        storage.delete(result[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()


def add_amenity(amenity_id=None):
    '''Adds a new amenity.'''
    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Data must be in JSON format')
    if 'name' not in data:
        raise BadRequest(description='Name is missing')
    new_amenity = Amenity(**data)
    new_amenity.save()
    return jsonify(new_amenity.to_dict()), 201


def update_amenity(amenity_id=None):
    '''Updates an amenity by ID.'''
    reserved_keys = ('id', 'created_at', 'updated_at')
    all_amenities = storage.all(Amenity).values()
    result = list(filter(lambda x: x.id == amenity_id, all_amenities))
    if result:
        data = request.get_json()
        if type(data) is not dict:
            raise BadRequest(description='Data must be in JSON format')
        old_amenity = result[0]
        for key, value in data.items():
            if key not in reserved_keys:
                setattr(old_amenity, key, value)
        old_amenity.save()
        return jsonify(old_amenity.to_dict()), 200
    raise NotFound()
