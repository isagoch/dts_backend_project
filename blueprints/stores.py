from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Store, Item
from schemas import StoreSchema, ItemSchema
stores_bp = Blueprint('stores', __name__)
@stores_bp.route('/', methods=['GET'])
def list_stores():
    return jsonify({"error": False, "data": StoreSchema(many=True).dump(Store.query.all())}), 200
@stores_bp.route('/<int:id>/items', methods=['GET'])
def list_items(id):
    query = Item.query.filter_by(store_id=id)
    if request.args.get('available', '').lower() == 'true': query = query.filter_by(availability=True)
    return jsonify({"error": False, "data": ItemSchema(many=True).dump(query.all())}), 200
@stores_bp.route('/items/<int:id>/availability', methods=['PUT'])
@jwt_required()
def toggle_availability(id):
    item = Item.query.get(id)
    item.availability = request.get_json()['availability']
    db.session.commit()
    return jsonify({"error": False, "message": "Availability updated"}), 200