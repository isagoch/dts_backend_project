from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from datetime import datetime
db = SQLAlchemy()
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if type(dbapi_connection).__name__ == "Connection":
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
class User(db.Model):
    __tablename__ = 'USER'
    user_id = db.Column("User_ID", db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column("First_Name", db.String(50))
    last_name = db.Column("Last_Name", db.String(50))
    email = db.Column("Email", db.String(100), unique=True, nullable=False)
    password_hash = db.Column("Password_Hash", db.String(255), nullable=False)
    phone_number = db.Column("Phone_Number", db.String(20))
    user_type = db.Column("User_Type", db.String(20), nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    __table_args__ = (db.CheckConstraint("User_Type IN ('customer', 'courier', 'both')", name="check_user_type"),)
class Customer(db.Model):
    __tablename__ = 'CUSTOMER'
    cust_id = db.Column("Cust_ID", db.Integer, db.ForeignKey('USER.User_ID', ondelete="CASCADE"), primary_key=True)
    hall = db.Column("Hall", db.String(100))
    room_number = db.Column("Room_Number", db.String(20))
    user = db.relationship("User", backref=db.backref("customer_profile", uselist=False))
class Courier(db.Model):
    __tablename__ = 'COURIER'
    cour_id = db.Column("Cour_ID", db.Integer, db.ForeignKey('USER.User_ID', ondelete="CASCADE"), primary_key=True)
    account_status = db.Column("Account_Status", db.String(20), default="active")
    current_balance = db.Column("Current_Balance", db.Numeric(10, 2), default=0.00)
    __table_args__ = (db.CheckConstraint("Account_Status IN ('active', 'suspended', 'inactive')", name="check_account_status"),)
    user = db.relationship("User", backref=db.backref("courier_profile", uselist=False))
class CourierCompensation(db.Model):
    __tablename__ = 'COURIER_COMPENSATION'
    cour_id = db.Column("Cour_ID", db.Integer, db.ForeignKey('COURIER.Cour_ID', ondelete="CASCADE"), primary_key=True)
    compensation_type = db.Column("Compensation_Type", db.String(50), primary_key=True)
    __table_args__ = (db.CheckConstraint("Compensation_Type IN ('fixed', 'percentage')", name="check_comp_type"),)
class Store(db.Model):
    __tablename__ = 'STORE'
    store_id = db.Column("Store_ID", db.Integer, primary_key=True)
    store_name = db.Column("Store_Name", db.String(100), nullable=False)
    location = db.Column("Location", db.String(200))
    closing_time = db.Column("Closing_Time", db.Time)
    items = db.relationship("Item", backref="store")
class Item(db.Model):
    __tablename__ = 'ITEM'
    item_id = db.Column("Item_ID", db.Integer, primary_key=True)
    store_id = db.Column("Store_ID", db.Integer, db.ForeignKey('STORE.Store_ID', ondelete="CASCADE"))
    item_name = db.Column("Item_Name", db.String(100), nullable=False)
    price = db.Column("Price", db.Numeric(8, 2), nullable=False)
    availability = db.Column("Availability", db.Boolean, default=True)
class Order(db.Model):
    __tablename__ = 'ORDER'
    order_id = db.Column("Order_ID", db.Integer, primary_key=True)
    customer_id = db.Column("Customer_ID", db.Integer, db.ForeignKey('CUSTOMER.Cust_ID'), index=True)
    delivery_id = db.Column("Delivery_ID", db.Integer, db.ForeignKey('DELIVERY.Delivery_ID'), nullable=True)
    order_timestamp = db.Column("Order_Timestamp", db.DateTime, default=datetime.utcnow)
    total_amount = db.Column("Total_Amount", db.Numeric(10, 2))
    order_status = db.Column("Order_Status", db.String(20), default="pending", index=True) 
    payment_status = db.Column("Payment_Status", db.String(20), default="pending")
    is_deleted = db.Column(db.Boolean, default=False)
    __table_args__ = (
        db.CheckConstraint("Order_Status IN ('pending', 'accepted', 'in_transit', 'delivered', 'cancelled', 'refunded')", name="check_order_status"),
        db.CheckConstraint("Payment_Status IN ('pending', 'completed', 'failed', 'refunded')", name="check_payment_status"),
    )
    details = db.relationship("OrderDetails", backref="order", cascade="all, delete-orphan")
class OrderDetails(db.Model):
    __tablename__ = 'ORDER_DETAILS'
    order_id = db.Column("Order_ID", db.Integer, db.ForeignKey('ORDER.Order_ID', ondelete="CASCADE"), primary_key=True)
    item_id = db.Column("Item_ID", db.Integer, db.ForeignKey('ITEM.Item_ID'), primary_key=True)
    quantity = db.Column("Quantity", db.Integer, nullable=False)
    item = db.relationship("Item")
class OrderPayment(db.Model):
    __tablename__ = 'ORDER_PAYMENT'
    payment_id = db.Column("Payment_ID", db.Integer, primary_key=True)
    order_id = db.Column("Order_ID", db.Integer, db.ForeignKey('ORDER.Order_ID', ondelete="CASCADE"))
    payment_method = db.Column("Payment_Method", db.String(50))
    amount = db.Column("Amount", db.Numeric(10, 2))
class Delivery(db.Model):
    __tablename__ = 'DELIVERY'
    delivery_id = db.Column("Delivery_ID", db.Integer, primary_key=True)
    courier_id = db.Column("Courier_ID", db.Integer, db.ForeignKey('COURIER.Cour_ID'), index=True, nullable=True)
    delivery_status = db.Column("Delivery_Status", db.String(20), default="unassigned", index=True)
    __table_args__ = (db.CheckConstraint("Delivery_Status IN ('unassigned', 'assigned', 'picked_up', 'delivered', 'returned')", name="check_delivery_status"),)
    orders = db.relationship("Order", backref="delivery_assignment")
class PromoCode(db.Model):
    __tablename__ = 'PROMO_CODE'
    code = db.Column("Code", db.String(50), primary_key=True)
    customer_id = db.Column("Customer_ID", db.Integer, db.ForeignKey('CUSTOMER.Cust_ID'))
    is_used = db.Column("Is_Used", db.Boolean, default=False)
    created_at = db.Column("Created_At", db.DateTime, default=datetime.utcnow)