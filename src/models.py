from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    years = db.Column(db.Integer, nullable=True)
    planet_id = db.Column(db.Integer, db.ForeignKey("planet.id"), nullable=False)
    favorite = db.relationship("Favorite", backref="character", lazy=True)

    def __repr__(self):
        return "<Planet %r>" % self.name

    def serialize(self):
        return {"id": self.id, "name": self.name}


class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    character = db.relationship("Character", backref="planet", lazy=True)
    favorite = db.relationship("Favorite", backref="planet", lazy=True)

    def __repr__(self):
        return "<Planet %r>" % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "habitans": list(map(lambda character: character.name, self.character)),
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    favorite = db.relationship("Favorite", backref="user", lazy=True)

    def __repr__(self):
        return "<User %r>" % self.name

    def serialize(self):
        return {"id": self.id, "name": self.name, "email": self.email}


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey("character.id"), nullable=True)
    planet_id = db.Column(db.Integer, db.ForeignKey("planet.id"), nullable=True)

    def __repr__(self):
        return "<Favorite %r>" % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user and self.user.serialize(),
            "character": self.character and self.character.serialize(),
            "planet": self.planet and self.planet.serialize(),
        }
