from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api
from sqlalchemy.orm import joinedload
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

def restaurant_to_dict(restaurant):
    return {
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [
            {
                "id": rp.id,
                "price": rp.price,
                "pizza": {
                    "id": rp.pizza.id,
                    "name": rp.pizza.name,
                    "ingredients": rp.pizza.ingredients
                }
            } for rp in restaurant.restaurant_pizzas
        ]
    }

def pizza_to_dict(pizza):
    return {
        "id": pizza.id,
        "name": pizza.name,
        "ingredients": pizza.ingredients,
    }

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    try:
        restaurants = Restaurant.query.all()
        return jsonify([
            {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
            } for restaurant in restaurants
        ])
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.options(joinedload(Restaurant.restaurant_pizzas).joinedload(RestaurantPizza.pizza)).filter_by(id=id).first()
    if restaurant is None:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    return jsonify(restaurant_to_dict(restaurant))

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if restaurant is None:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    db.session.delete(restaurant)
    db.session.commit()
    return '', 204

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza_to_dict(pizza) for pizza in pizzas])

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    if not data or "pizza_id" not in data or "restaurant_id" not in data or "price" not in data:
        return make_response(jsonify({"errors": ["Missing data"]}), 400)
    if data["price"] < 1 or data["price"] > 30:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)  # Updated message
    pizza = Pizza.query.filter_by(id=data["pizza_id"]).first()
    restaurant = Restaurant.query.filter_by(id=data["restaurant_id"]).first()
    if pizza is None or restaurant is None:
        return make_response(jsonify({"errors": ["Pizza or Restaurant not found"]}), 404)
    try:
        restaurant_pizza = RestaurantPizza(pizza_id=data["pizza_id"], restaurant_id=data["restaurant_id"], price=data["price"])
        db.session.add(restaurant_pizza)
        db.session.commit()
        return jsonify(restaurant_pizza.to_dict()), 201
    except Exception:
        return make_response(jsonify({"errors": ["Internal server error"]}), 500)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

if __name__ == "__main__":
    app.run(port=5555, debug=True)