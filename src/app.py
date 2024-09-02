"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorite, Planet, Character

# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url.replace(
        "postgres://", "postgresql://"
    )
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# generate sitemap with all your endpoints
@app.route("/")
def sitemap():
    return generate_sitemap(app)


@app.route("/user", methods=["GET"])
def get_users():
    try:
        all_users = User.query.all()
        users = list(map(lambda user: user.serialize(), all_users))
        return jsonify(users), 200
    except Exception as e:
        return jsonify(str(e)), 404


@app.route("/planet", methods=["GET"])
def get_planet():
    try:
        all_planet = Planet.query.all()
        planet = list(map(lambda planet: planet.serialize(), all_planet))
        return jsonify(planet), 200
    except Exception as e:
        return jsonify(str(e)), 404


@app.route("/people", methods=["GET"])
def get_character():
    try:
        all_character = Character.query.all()
        character = list(map(lambda planet: planet.serialize(), all_character))
        return jsonify(character), 200
    except Exception as e:
        return jsonify(str(e)), 404


@app.route("/people/<int:character_id>", methods=["GET"])
def get_selected_character(character_id):
    try:
        find_character = Character.query.filter_by(id=character_id).first().serialize()
        return jsonify(find_character), 200
    except Exception as e:
        return jsonify(str(e)), 404


@app.route("/planet/<int:planet_id>", methods=["GET"])
def get_selected_planet(planet_id):
    try:
        find_planet = Planet.query.filter_by(id=planet_id).first().serialize()
        return jsonify(find_planet), 200
    except Exception as e:
        return jsonify(str(e)), 404


@app.route("/users/favorites/<int:user_id>", methods=["GET"])
def get_selected_favorite(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        planet_favorites = list( map(lambda fav: fav.planet.serialize(), filter(lambda fav: fav.planet, user.favorite)))
        character_favorites = list(map(lambda fav: fav.character.serialize(), filter(lambda fav: fav.character, user.favorite)))

        response = {
            "user": user.serialize(),
            "planets": planet_favorites,
            "characters": character_favorites,
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500



@app.route("/favorite/planet/<int:planet_id>/<int:user_id>/", methods=["GET"])
def add_planet_favorite(user_id, planet_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        planet = Planet.query.filter_by(id=planet_id).first()

        if not user or not planet:
            return jsonify({"message:usuario o planeta no encontrado"}), 200

        new_favorite_planet = Favorite(user_id=user.id, planet_id=planet.id)
        db.session.add(new_favorite_planet)
        db.session.commit()

        return jsonify({"message": f"El usuario {user.name} a añadido a sus favoritos el planet {planet.name}"}),200

    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500

@app.route("/favorite/people/<int:people_id>/<int:user_id>/", methods=["GET"])
def add_people_favorite(user_id, people_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        character = Character.query.filter_by(id=people_id).first()

        if not user or not character:
            return jsonify({"message:usuario o personaje no encontrado"}), 200

        new_favorite_planet = Favorite(user_id=user.id, character_id=character.id)
        db.session.add(new_favorite_planet)
        db.session.commit()

        return jsonify({"message": f"El usuario {user.name} a añadido a sus favoritos el personaje {character.name}"}),200

    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500



# this only runs if `$ python src/app.py` is executed
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT, debug=False)
