#!/usr/bin/env python3
from flask import Flask, request
from flask_restful import Api, Resource
from flask_migrate import Migrate
from models import db, Restaurant, RestaurantPizza, Pizza
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class RestaurantListResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [r.to_dict(rules=('-restaurant_pizzas',)) for r in restaurants], 200

class RestaurantDetailResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404

        return restaurant.to_dict(rules=(
            '-pizzas',
            'restaurant_pizzas',
            'restaurant_pizzas.pizza'
        )), 200

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404

        db.session.delete(restaurant)
        db.session.commit()
        return {}, 204

class PizzaListResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict(rules=('-restaurant_pizzas',)) for pizza in pizzas], 200

class RestaurantPizzaListResource(Resource):
    def post(self):
        data = request.get_json()

        try:
            price = data.get('price')
            pizza_id = data.get('pizza_id')
            restaurant_id = data.get('restaurant_id')

            new_rp = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )

            db.session.add(new_rp)
            db.session.commit()

            return new_rp.to_dict(rules=('pizza', 'restaurant')), 201

        except Exception as e:
            return {"errors": [str(e)]}, 400

# Route registration
api.add_resource(RestaurantListResource, '/restaurants')
api.add_resource(RestaurantDetailResource, '/restaurants/<int:id>')
api.add_resource(PizzaListResource, '/pizzas')
api.add_resource(RestaurantPizzaListResource, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
