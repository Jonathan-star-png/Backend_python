from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash # nos permite recibir y cifrar las contraseñas, verificar las contraseñas
from bson import json_util #nos permite convertir del formato bson a json
from bson.objectid import ObjectId 
import json
from datetime import datetime
from os import environ
app = Flask(__name__)
app.config['MONGO_URI']=environ.get("MONGO_URI")
mongo = PyMongo(app)

def create_user(username,email,hashed_password,active,creationDate):
    
        #insertamos en la colección
    id = mongo.db.users.insert(
        {'username':username, 'email':email, 'password':hashed_password, 'active':active, 'creationDate':creationDate}
    )

    #respuesta cuando creamos el usuario
    response={
        'id': str(id),
        'username':username,
        'email':email,
        'password':hashed_password,
        'active':active,
        'creationDate':creationDate
    }
    return response

def get_users():
    users = mongo.db.users.find()
    # convertir de bson a json
    response = json_util.dumps(users)
    return Response(response, mimetype='application/json')

def filter_active(active):
    users = mongo.db.users.find({'active':active})
    response = json_util.dumps(users)
    return Response(response, mimetype='application/json')

def filter_date(key,values):
    if key[1]=='>':
        filter=mongo.db.users.find({key[0]:{"$gte": (values)}})
    if key[1]=='<':
        filter=mongo.db.users.find({key[0]:{"$lte": (values)}})     
    response = json_util.dumps(filter)
    return Response(response, mimetype='application/json')

def filter_active_date(active,key,values):
    if key[1]=='>':
        filter=mongo.db.users.find({"$and":[{"active":active},{key[0]:{"$gte": (values)}}]})
    if key[1]=='<':
        filter=mongo.db.users.find({"$and":[{"active":active},{key[0]:{"$lte": (values)}}]})   
    response = json_util.dumps(filter)
    return Response(response, mimetype='application/json')

def get_user(id):
    user = mongo.db.users.find_one({'_id':ObjectId(id)}) #convertimos el id string a un ObjectId
    response = json_util.dumps(user)
    return Response(response, mimetype="application/json")

def delete_user(id):
    mongo.db.users.delete_one({'_id': ObjectId(id)})
    response = jsonify({'message':'User ' + id + ' was Deleted successfully'}) 
    return response

def update_user(id,username,hashed_password,email,active,creationDate):
    mongo.db.users.update_one({'_id':ObjectId(id)}, {'$set':{
            'username':username,
            'password':hashed_password,
            'email':email,
            'active':active,
            'creationDate':creationDate
        }})
    response = jsonify({'message': 'User ' + id + 'was update successfully'})
    return response
