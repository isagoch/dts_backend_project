from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, Customer, Courier
from schemas import UserSchema
from marshmallow import ValidationError
auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = UserSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": True, "details": err.messages}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": True, "message": "Email exists"}), 409
    user = User(
        first_name=data['first_name'], last_name=data['last_name'],
        email=data['email'], password_hash=generate_password_hash(data['password']),
        phone_number=data.get('phone_number'), user_type=data['user_type']
    )
    db.session.add(user)
    db.session.flush()
    if data['user_type'] in ['customer', 'both']: db.session.add(Customer(cust_id=user.user_id))
    if data['user_type'] in ['courier', 'both']: db.session.add(Courier(cour_id=user.user_id))
    db.session.commit()
    return jsonify({"error": False, "message": "Registered"}), 201
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not check_password_hash(user.password_hash, data.get('password')):
        return jsonify({"error": True, "message": "Invalid credentials"}), 401
    return jsonify({"error": False, "token": create_access_token(identity=str(user.user_id))}), 200
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    return jsonify({"error": False, "data": UserSchema(exclude=("password",)).dump(user)}), 200