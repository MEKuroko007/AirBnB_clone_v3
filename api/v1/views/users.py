#!/usr/bin/python3
"""Defines views for handling users in the API."""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.user import User


@app_views.route('/users/', methods=['GET'])
@app_views.route('/users', methods=['GET'])
def list_users():
    """Retrieves a list of all users."""
    list_users = [user.to_dict() for user in storage.all(User).values()]
    return jsonify(list_users)


@app_views.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Retrieves a specific user."""
    user_obj = storage.get(User, user_id)
    if not user_obj:
        abort(404)
    return jsonify(user_obj.to_dict())


@app_views.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Deletes a user."""
    user_obj = storage.get(User, user_id)
    if not user_obj:
        abort(404)
    storage.delete(user_obj)
    storage.save()
    return jsonify({}), 200


@app_views.route('/users/', methods=['POST'])
def create_user():
    """Creates a new user."""
    data = request.get_json()
    if not data:
        abort(400, 'Not a JSON')
    if 'email' not in data or 'password' not in data:
        abort(400, 'Missing email or password')
    new_user = User(email=data['email'], password=data['password'])
    storage.new(new_user)
    storage.save()
    return jsonify(new_user.to_dict()), 201


@app_views.route('/users/<user_id>', methods=['PUT'])
def updates_user(user_id):
    """Updates a user."""
    user_obj = storage.get(User, user_id)
    if not user_obj:
        abort(404)
    data = request.get_json()
    if not data:
        abort(400, 'Not a JSON')
    if 'first_name' in data:
        user_obj.first_name = data['first_name']
    if 'last_name' in data:
        user_obj.last_name = data['last_name']
    storage.save()
    return jsonify(user_obj.to_dict()), 200
