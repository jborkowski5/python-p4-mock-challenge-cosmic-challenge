#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/scientists', methods = ['GET'])
def scientists():
    scientists = Scientist.query.all()

    scientists_dict = [scientist.to_dict(rules = ('-missions', )) for scientist in scientists]

    response = make_response(
        scientists_dict,
        200
    )

    return response

@app.route('/scientists/<int:id>', methods = ['GET', 'PATCH', 'DELETE'])
def scientist_by_id(id):
    scientist = Scientist.query.filter(Scientist.id == id).first()

    if scientist:
        if request.method == 'GET':
            response = make_response(
                scientist.to_dict(),
                200
            )

        elif request.method == 'PATCH':
            form_data = request.get_json()

            try:
                for attr in form_data:
                    setattr(scientist, attr, form_data.get(attr))

                db.session.commit()

                response = make_response(
                    scientist.to_dict(rules = ('-missions', )),
                    202
                )

            except ValueError:
                response = make_response(
                    { "errors": ["validation errors"] },
                    400
                )

                return response
            
        elif request.method == 'DELETE':
            try:
                if scientist:
                    db.session.delete(scientist)

                db.session.commit()

                response = make_response(
                    {},
                    204
                )
            except ValueError:
                response = make_response(
                    { "errors": ["validation errors"] },
                    400
                )
        return response
    else:
        response = make_response(
            { "error": "Scientist not found" },
            404
        )

    return response


@app.route('/scientists', methods = ['POST'])
def new_scientists():
    form_data = request.get_json()

    try:
        new_scientist_obj = Scientist(
            name = form_data['name'],
            field_of_study = form_data['field_of_study']
        )

        db.session.add(new_scientist_obj)

        db.session.commit()

        response = make_response(
            new_scientist_obj.to_dict(),
            201
        )

    except ValueError:
        response = make_response(
            { "errors": ["validation errors"] },
            400
        )

        return response
    
    return response

@app.route('/planets', methods = ['GET'])
def planets():
    planets = Planet.query.all()

    planets_dict = [planet.to_dict(rules = ('-missions', )) for planet in planets]

    response = make_response(
        planets_dict,
        200
    )

    return response

@app.route('/missions', methods = ['POST'])
def new_missions():
    form_data = request.get_json()

    try:
        new_mission_obj = Mission(
            name = form_data['name'],
            scientist_id = form_data['scientist_id'],
            planet_id = form_data['planet_id']
        )

        db.session.add(new_mission_obj)

        db.session.commit()

        response = make_response(
            new_mission_obj.to_dict(),
            201
        )

    except ValueError:
        response = make_response(
            { "errors": ["validation errors"] },
            400
        )

        return response
    
    return response


if __name__ == '__main__':
    app.run(port=5555, debug=True)
