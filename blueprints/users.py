from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User
from schemas import UserSchema
users_bp = Blueprint('users', __name__)
@users_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_profile(id):
    if int(get_jwt_identity()) != id: return jsonify({"error": True, "message": "Forbidden"}), 403
    user = User.query.get(id)
    data = UserSchema(partial=True, exclude=("password", "user_type", "email")).load(request.get_json())
    
    if 'first_name' in data: user.first_name = data['first_name']
    if 'last_name' in data: user.last_name = data['last_name']
    if 'phone_number' in data: user.phone_number = data['phone_number']
    db.session.commit()
    return jsonify({"error": False, "message": "Updated"}), 200
@users_bp.route('/<int:id>/roles', methods=['GET'])
@jwt_required()
def get_roles(id):
    user = User.query.get(id)
    return jsonify({"error": False, "roles": [user.user_type]}), 200