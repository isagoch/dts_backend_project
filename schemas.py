from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
ma = Marshmallow()
class UserSchema(ma.Schema):
    user_id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
    phone_number = fields.Str(validate=validate.Length(max=20))
    user_type = fields.Str(required=True, validate=validate.OneOf(["customer", "courier", "both"]))
class ItemSchema(ma.Schema):
    item_id = fields.Int(dump_only=True)
    store_id = fields.Int()
    item_name = fields.Str()
    price = fields.Decimal(as_string=True)
    availability = fields.Bool()
class StoreSchema(ma.Schema):
    store_id = fields.Int(dump_only=True)
    store_name = fields.Str()
    location = fields.Str()
    closing_time = fields.Time()
    items = fields.List(fields.Nested(ItemSchema))
class OrderItemInputSchema(ma.Schema):
    item_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
class PlaceOrderSchema(ma.Schema):
    items = fields.List(fields.Nested(OrderItemInputSchema), required=True, validate=validate.Length(min=1))
class OrderDetailsSchema(ma.Schema):
    item = fields.Nested(ItemSchema)
    quantity = fields.Int()
class OrderSchema(ma.Schema):
    order_id = fields.Int(dump_only=True)
    customer_id = fields.Int()
    delivery_id = fields.Int(allow_none=True)
    order_timestamp = fields.DateTime()
    total_amount = fields.Decimal(as_string=True)
    order_status = fields.Str()
    payment_status = fields.Str()
    details = fields.List(fields.Nested(OrderDetailsSchema))
class PaymentInputSchema(ma.Schema):
    order_id = fields.Int(required=True)
    payment_method = fields.Str(required=True, validate=validate.OneOf(["card", "transfer"]))
class PaymentSchema(ma.Schema):
    payment_id = fields.Int(dump_only=True)
    order_id = fields.Int()
    payment_method = fields.Str()
    amount = fields.Decimal(as_string=True)
class RefundInputSchema(ma.Schema):
    order_id = fields.Int(required=True)
    amount = fields.Decimal(required=False)
class ItemUnavailableSchema(ma.Schema):
    item_id = fields.Int(required=True)
class DeliveryStatusSchema(ma.Schema):
    status = fields.Str(required=True, validate=validate.OneOf(["picked_up", "delivered", "returned"]))
class DamageClaimSchema(ma.Schema):
    amount = fields.Decimal(required=True, validate=validate.Range(min=0))