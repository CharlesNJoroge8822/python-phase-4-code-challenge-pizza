from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # Relationship with RestaurantPizza
    restaurant_pizzas = db.relationship("RestaurantPizza", back_populates="restaurant", cascade="all, delete-orphan")

    # Serialization rules
    serialize_rules = ("-restaurant_pizzas.restaurant",)

    # Validations
    @validates("name")
    def validate_name(self, key, value):
        if not value or len(value.strip()) < 3:
            raise ValueError("Restaurant name must be at least 3 characters long.")
        return value.strip()

    @validates("address")
    def validate_address(self, key, value):
        if not value or len(value.strip()) < 5:
            raise ValueError("Address must be at least 5 characters long.")
        return value.strip()

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # Relationship with RestaurantPizza
    restaurant_pizzas = db.relationship("RestaurantPizza", back_populates="pizza")

    # Serialization rules
    serialize_rules = ("-restaurant_pizzas.pizza",)

    # Validations
    @validates("name")
    def validate_name(self, key, value):
        if not value or len(value.strip()) < 4:
            raise ValueError("Pizza name must be at least 4 characters long.")
        return value.strip()

    @validates("ingredients")
    def validate_ingredients(self, key, value):
        if not value or len(value.strip()) < 4:
            raise ValueError("Ingredients must be at least 4 characters long.")
        return value.strip()

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # Foreign keys
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=False)

    # Relationships
    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")

    # Serialization rules
    serialize_rules = ("-restaurant.restaurant_pizzas", "-pizza.restaurant_pizzas")

    # Validation
    @validates("price")
    def validate_price(self, key, value):
        if value is None or not (1 <= value <= 30):
            raise ValueError("Price must be between 1 and 30.")
        return value

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
