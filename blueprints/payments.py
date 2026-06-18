from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Order, OrderPayment
from schemas import PaymentInputSchema, PaymentSchema, RefundInputSchema
payments_bp = Blueprint('payments', __name__)
@payments_bp.route('/', methods=['POST'])
@jwt_required()
def initiate_payment():
    data = PaymentInputSchema().load(request.get_json())
    order = Order.query.get(data['order_id'])
    payment = OrderPayment(order_id=order.order_id, payment_method=data['payment_method'], amount=order.total_amount)
    db.session.add(payment)
    order.payment_status = "completed"
    db.session.commit()
    return jsonify({"error": False, "message": "Payment successful"}), 200
@payments_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_payment(order_id):
    return jsonify({"error": False, "data": PaymentSchema().dump(OrderPayment.query.filter_by(order_id=order_id).first())}), 200
@payments_bp.route('/refund', methods=['POST'])
@jwt_required()
def issue_refund():
    data = RefundInputSchema().load(request.get_json())
    order = Order.query.get(data['order_id'])
    if 'amount' in data and data['amount'] < order.total_amount: order.total_amount -= data['amount']
    else: order.payment_status = "refunded"
    db.session.commit()
    return jsonify({"error": False, "message": "Refund processed"}), 200