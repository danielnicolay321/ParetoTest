from flask import Flask, request, jsonify, url_for, abort
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_httpauth import HTTPBasicAuth

from passlib.apps import custom_app_context as pwd_context

from datetime import datetime

import os
import json

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crud.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
auth = HTTPBasicAuth()

class Climate(db.Model):
    __tablename__ = 'climateInfos'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    rainfall = db.Column(db.Integer)
    temperature = db.Column(db.Integer)

    def __init__(self, date, rainfall, temperature):
        self.date = date
        self.rainfall = rainfall
        self.temperature = temperature


class ClimateSchema(ma.Schema):
    class Meta:
        fields = ('date', 'rainfall', 'temperature')


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


db.create_all()

climate_schema = ClimateSchema()
climate_schema = ClimateSchema(many=True)

def serializeClimate(self):
    return {
        'id': self.id,
        'date': self.date, 
        'rainfall': self.rainfall,
        'temperature': self.temperature,
    }

def serializeUser(self):
    return{
        'id': self.id,
        'username': self.username
    }

def serializeError(self):
    return {
        'message': self
    }


# endpoint to create new climate
@app.route("/climate", methods=["POST"])
@auth.login_required
def add_user():
    date = datetime.strptime(request.json['date'], '%Y-%m-%d')
    rainfall = request.json['rainfall']
    temperature = request.json['temperature']
    new_climate = Climate(date, rainfall, temperature)
    db.session.add(new_climate)
    db.session.commit()
    return jsonify(serializeClimate(new_climate))

# endpoint to show all climates
@app.route("/climate", methods=["GET"])
def get_climate():
    all_climates1 = []
    if request.args is None:
        all_climates = Climate.query.all()
        result = climate_schema.dump(all_climates)
        return jsonify(result)
    
    if 'date' in request.args:
        try:
            rst = Climate.query.filter_by(date=\
                datetime.now().date()).first()
            for rslt in rst:
                all_climates1.append(rslt)                     
        except:
            return jsonify(serializeError("No data"))

    if 'rainfall' in request.args:
        try:
            rst = Climate.query.filter_by(rainfall=\
                request.args['rainfall'])
            for rslt in rst:
                all_climates1.append(rslt)
        except:
            return jsonify(serializeError("No data"))

    if 'temperature' in request.args:
        try:
            rst = Climate.query.filter_by(temperature=\
                request.args['temperature'])
            for rslt in rst:
                all_climates1.append(rslt)
        except:
            return jsonify(serializeError("No data"))

    try:
        result = climate_schema.dump(all_climates1)
        return jsonify(result)
    except:
        return jsonify(serializeError("unexpected error"))

# endpoint to get climate detail by id
@app.route("/climate/<id>", methods=["GET"])
def climate_detail(id):
    climate = Climate.query.get(id)
    return jsonify(serializeClimate(climate))

# endpoint to update climate
@app.route("/climate/<id>", methods=["PUT"])
@auth.login_required
def climate_update(id):
    climate = Climate.query.get(id)
    date = request.json['date']
    rainfall = request.json['rainfall']
    temperature = request.json['temperature']
    climate.date = date
    climate.rainfall = rainfall
    climate.temperature = temperature
    db.session.commit()
    return climate_schema.jsonify(climate)

# endpoint to delete climate
@app.route("/climate/<id>", methods=["DELETE"])
@auth.login_required
def climate_delete(id):
    climate = Climate.query.get(id)
    db.session.delete(climate)
    db.session.commit()
    return jsonify(serializeError("The item has been deleted"))

# endpoint to predict
@app.route("/climate/predict", methods=["GET"])
def climate():
    climate = Climate.query.filter_by(date=datetime.now().date()).first()
    if climate is not None:
        return jsonify(serializeClimate(climate))
    else:
        abort(404)

#endpoint to register a new user
@app.route("/users", methods=["POST"])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)
    if User.query.filter_by(username = username).first() is not None:
        abort(400)
    user = User(username = username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username}, 201, {'Location':\
        url_for('get_user', id=user.id, _external=True)})

#endpoint to get user by id
@app.route("/users/<id>", methods=["GET"])
def get_user(id):
    user = User.query.get(id)
    if user is not None:
        return jsonify(serializeUser(user))
    else:
        abort(404)

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username = username).first()
    if not user or not user.verify_password(password):
        return False
    else:
        return True

if __name__ == '__main__':
    app.run(debug=True)