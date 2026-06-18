from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, PromoCode
import secrets
promos_bp = Blueprint('promos', __name__)
@promos_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_code():
    customer_id = request.get_json().get('customer_id')
    code = "FREE-" + secrets.token_hex(4).upper()
    db.session.add(PromoCode(code=code, customer_id=customer_id))
    db.session.commit()
    return jsonify({"error": False, "data": {"code": code}}), 201
@promos_bp.route('/<string:code>/validate', methods=['GET'])
@jwt_required()
def validate_code(code):
    promo = PromoCode.query.get(code)
    if not promo or promo.is_used: return jsonify({"error": True}), 400
    return jsonify({"error": False, "message": "Valid code"}), 200
@promos_bp.route('/<string:code>/redeem', methods=['PUT'])
@jwt_required()
def redeem_code(code):
    promo = PromoCode.query.get(code)
    promo.is_used = True
    db.session.commit()
    return jsonify({"error": False}), 200