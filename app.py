import os
import datetime
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from models import db, Store, Item
from schemas import ma
from blueprints.auth import auth_bp
from blueprints.users import users_bp
from blueprints.stores import stores_bp
from blueprints.orders import orders_bp
from blueprints.deliveries import deliveries_bp
from blueprints.payments import payments_bp
from blueprints.promos import promos_bp
from dotenv import load_dotenv

load_dotenv()
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chowdome.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
    db.init_app(app)
    ma.init_app(app)
    jwt = JWTManager(app)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(stores_bp, url_prefix='/stores')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(deliveries_bp, url_prefix='/deliveries')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(promos_bp, url_prefix='/promo-codes')
    @app.errorhandler(400)
    def bad_request(error): return jsonify({"error": True, "message": "Bad Request", "code": "400"}), 400
    @app.errorhandler(401)
    def unauthorized(error): return jsonify({"error": True, "message": "Unauthorized", "code": "401"}), 401
    @app.errorhandler(403)
    def forbidden(error): return jsonify({"error": True, "message": "Forbidden", "code": "403"}), 403
    @app.errorhandler(404)
    def not_found(error): return jsonify({"error": True, "message": "Not Found", "code": "404"}), 404
    @app.errorhandler(500)
    def internal_error(error): return jsonify({"error": True, "message": "Internal Server Error", "code": "500"}), 500
    @app.cli.command("seed-db")
    def seed_db():
        db.create_all()
        stores_data = [
            {"name": "Combos", "location": "Cafeteria Main Hall", "time": datetime.time(19, 0), "items": [("Rice & Beans Combo", 1500.00), ("Spaghetti Combo", 1200.00)]},
            {"name": "6:33 Pizza", "location": "Cafeteria Wing A", "time": datetime.time(19, 0), "items": [("Pepperoni Pizza", 4500.00), ("Margherita Pizza", 4000.00)]},
            {"name": "Borito Chicken", "location": "Cafeteria Wing B", "time": datetime.time(19, 0), "items": [("Fried Chicken (2 Pieces)", 2000.00), ("Chicken Burger", 2500.00)]},
            {"name": "Breadwarmer", "location": "Cafeteria Entrance", "time": datetime.time(19, 0), "items": [("Meat Pie", 800.00), ("Sausage Roll", 600.00)]},
            {"name": "Choice Waffles", "location": "Cafeteria Wing C", "time": datetime.time(19, 0), "items": [("Classic Belgian Waffle", 1500.00), ("Chocolate Chip Waffle", 1800.00)]},
            {"name": "Waffledom", "location": "Cafeteria Wing C", "time": datetime.time(19, 0), "items": [("Strawberry Waffle", 2000.00), ("Nutella Waffle", 2200.00)]}
        ]
        
        for data in stores_data:
            store = Store.query.filter_by(store_name=data["name"]).first()
            if not store:
                store = Store(store_name=data["name"], location=data["location"], closing_time=data["time"])
                db.session.add(store)
                db.session.flush()
            for item_name, item_price in data["items"]:
                if not Item.query.filter_by(item_name=item_name, store_id=store.store_id).first():
                    db.session.add(Item(store_id=store.store_id, item_name=item_name, price=item_price))
        
        db.session.commit()
        print("Database seeded successfully.")
    return app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)