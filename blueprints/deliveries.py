from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, Delivery, Courier
from schemas import OrderSchema, DeliveryStatusSchema, DamageClaimSchema
deliveries_bp = Blueprint('deliveries', __name__)
@deliveries_bp.route('/available', methods=['GET'])
@jwt_required()
def available_deliveries():
    orders = Order.query.filter_by(delivery_id=None, order_status="pending").all()
    return jsonify({"error": False, "data": OrderSchema(many=True).dump(orders)}), 200
@deliveries_bp.route('/<int:order_id>/accept', methods=['POST'])
@jwt_required()
def accept_delivery(order_id):
    current_user = get_jwt_identity()
    order = Order.query.get(order_id)
    delivery = Delivery(courier_id=current_user['id'], delivery_status="assigned")
    db.session.add(delivery)
    db.session.flush()
    order.delivery_id = delivery.delivery_id
    order.order_status = "accepted"
    db.session.commit()
    return jsonify({"error": False, "message": "Accepted"}), 200
@deliveries_bp.route('/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_status(id):
    delivery = Delivery.query.get(id)
    data = DeliveryStatusSchema().load(request.get_json())
    delivery.delivery_status = data['status']
    for order in Order.query.filter_by(delivery_id=id).all():
        if data['status'] == 'picked_up': order.order_status = "in_transit"
        elif data['status'] == 'delivered': order.order_status = "delivered"
        elif data['status'] == 'returned': order.order_status = "cancelled"
    db.session.commit()
    return jsonify({"error": False, "message": "Updated"}), 200
@deliveries_bp.route('/<int:id>/damage-claim', methods=['POST'])
@jwt_required()
def damage_claim(id):
    data = DamageClaimSchema().load(request.get_json())
    delivery = Delivery.query.get(id)
    courier = Courier.query.get(delivery.courier_id)
    courier.current_balance -= data['amount']
    db.session.commit()
    return jsonify({"error": False, "message": "Claim logged"}), 200
@deliveries_bp.route('/couriers/<int:id>/balance', methods=['GET'])
@jwt_required()
def courier_balance(id):
    courier = Courier.query.get(id)
    return jsonify({"error": False, "balance": float(courier.current_balance)}), 200