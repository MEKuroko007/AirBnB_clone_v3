#!/usr/bin/python3
"""Defines views for handling places amenities in the API."""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.place import Place
from models.amenity import Amenity


@app_views.route('/places/<place_id>/amenities', methods=['GET'])
@app_views.route('/places/<place_id>/amenities/', methods=['GET'])
def list_amenities_of_place(place_id):
    """Retrieves a list of amenities for a given place."""
    all_places = storage.all(Place).values()
    place_obj = next((place for place
                      in all_places if place.id == place_id), None)
    if not place_obj:
        abort(404)
    list_amenities = [amenity.to_dict() for amenity in place_obj.amenities]
    return jsonify(list_amenities)


@app_views.route('/places/<place_id>/amenities/<amenity_id>', methods=['POST'])
def create_place_amenity(place_id, amenity_id):
    """Associates an amenity with a place."""
    place_obj = storage.get(Place, place_id)
    if not place_obj:
        abort(404)
    amenity_obj = storage.get(Amenity, amenity_id)
    if not amenity_obj:
        abort(404)
    if amenity_obj in place_obj.amenities:
        return jsonify(amenity_obj.to_dict()), 200
    place_obj.amenities.append(amenity_obj)
    storage.save()
    return jsonify(amenity_obj.to_dict()), 201


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 methods=['DELETE'])
def delete_place_amenity(place_id, amenity_id):
    """Disassociates an amenity from a place."""
    place_obj = storage.get(Place, place_id)
    if not place_obj:
        abort(404)
    amenity_obj = storage.get(Amenity, amenity_id)
    if not amenity_obj:
        abort(404)
    if amenity_obj not in place_obj.amenities:
        abort(404)
    place_obj.amenities.remove(amenity_obj)
    storage.save()
    return jsonify({}), 200


@app_views.route('/amenities/<amenity_id>', methods=['GET'])
def get_place_amenity(amenity_id):
    """Retrieves a specific amenity."""
    amenity_obj = storage.get(Amenity, amenity_id)
    if not amenity_obj:
        abort(404)
    return jsonify(amenity_obj.to_dict())
