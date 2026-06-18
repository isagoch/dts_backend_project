from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, OrderDetails, User, Item
from schemas import PlaceOrderSchema, OrderSchema, ItemUnavailableSchema
from datetime import datetime
orders_bp = Blueprint('orders', __name__)
@orders_bp.route('/', methods=['POST'])
@jwt_required()
def place_order():
    current_user_id = get_jwt_identity()
    if datetime.now().hour >= 19: return jsonify({"error": True, "message": "Orders only allowed 12:00 AM - 7:00 PM"}), 400

    user = User.query.get(int(current_user_id))
    if not user or not user.phone_number or not user.email: return jsonify({"error": True, "message": "Phone & Email required"}), 400
    if user.user_type not in ['customer', 'both']: return jsonify({"error": True, "message": "Forbidden"}), 403
    data = PlaceOrderSchema().load(request.get_json())
    total_amount, order_details_list = 0, []
    for item_data in data['items']:
        item = Item.query.get(item_data['item_id'])
        if not item or not item.availability: return jsonify({"error": True, "message": f"Item {item_data['item_id']} unavailable"}), 400
        total_amount += item.price * item_data['quantity']
        order_details_list.append(OrderDetails(item_id=item.item_id, quantity=item_data['quantity']))
    new_order = Order(customer_id=user.user_id, total_amount=total_amount)
    db.session.add(new_order)
    db.session.flush()
    for detail in order_details_list:
        detail.order_id = new_order.order_id
        db.session.add(detail)
    db.session.commit()
    return jsonify({"error": False, "order_id": new_order.order_id}), 201
@orders_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_order(id):
    return jsonify({"error": False, "data": OrderSchema().dump(Order.query.get(id))}), 200
@orders_bp.route('/customer/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer_orders(customer_id):
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.order_timestamp.desc()).all()
    return jsonify({"error": False, "data": OrderSchema(many=True).dump(orders)}), 200
@orders_bp.route('/<int:id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_order(id):
    order = Order.query.get(id)
    if order.customer_id != int(get_jwt_identity()) or order.delivery_id: return jsonify({"error": True}), 400
    order.order_status = "cancelled"
    if order.payment_status == "completed": order.payment_status = "refunded"
    db.session.commit()
    return jsonify({"error": False, "message": "Cancelled"}), 200
@orders_bp.route('/<int:id>/item-unavailable', methods=['PUT'])
@jwt_required()
def report_item_unavailable(id):
    data = ItemUnavailableSchema().load(request.get_json())
    order = Order.query.get(id)
    detail = OrderDetails.query.filter_by(order_id=id, item_id=data['item_id']).first()
    refund = detail.item.price * detail.quantity
    order.total_amount -= refund
    db.session.commit()
    return jsonify({"error": False, "message": f"Refunded {refund}"}), 200