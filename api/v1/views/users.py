#!/usr/bin/python3
'''Defines views for managing users within the API.'''
from flask import jsonify, request
from werkzeug.exceptions import NotFound, BadRequest

from api.v1.views import app_views
from models import storage
from models.user import User


@app_views.route('/users', methods=['GET'])
@app_views.route('/users/<user_id>', methods=['GET'])
def get_users(user_id=None):
    '''Handles requests to retrieve users.'''
    if user_id:
        user = storage.get(User, user_id)
        if user:
            user_data = user.to_dict()
            remove_sensitive_data(user_data)
            return jsonify(user_data)
        raise NotFound()
    all_users = storage.all(User).values()
    users = [remove_sensitive_data(user.to_dict()) for user in all_users]
    return jsonify(users)


def remove_sensitive_data(user_data):
    '''Removes sensitive data from user data.'''
    sensitive_fields = ['places', 'reviews']
    for field in sensitive_fields:
        user_data.pop(field, None)
    return user_data


@app_views.route('/users/<user_id>', methods=['DELETE'])
def remove_user(user_id):
    '''Handles requests to delete a user.'''
    user = storage.get(User, user_id)
    if user:
        storage.delete(user)
        storage.save()
        return jsonify({}), 200
    raise NotFound()


@app_views.route('/users', methods=['POST'])
def add_user():
    '''Handles requests to add a new user.'''
    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Data must be in JSON format')
    if 'email' not in data:
        raise BadRequest(description='Email is missing')
    if 'password' not in data:
        raise BadRequest(description='Password is missing')
    user = User(**data)
    user.save()
    user_data = user.to_dict()
    remove_sensitive_data(user_data)
    return jsonify(user_data), 201


@app_views.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    '''Handles requests to update a user.'''
    reserved_keys = ('id', 'email', 'created_at', 'updated_at')
    user = storage.get(User, user_id)
    if user:
        data = request.get_json()
        if type(data) is not dict:
            raise BadRequest(description='Data must be in JSON format')
        for key, value in data.items():
            if key not in reserved_keys:
                setattr(user, key, value)
        user.save()
        user_data = user.to_dict()
        remove_sensitive_data(user_data)
        return jsonify(user_data), 200
    raise NotFound()
