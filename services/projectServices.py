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

def create_project(projectName,projectType,userId,active,creationDate,description):
    id = mongo.db.projects.insert(
            {'projectName':projectName, 'projectType':projectType, 'userId':userId,'active':active,'creationDate':creationDate,'description':description}
        )
    response={
            'id': str(id),
            'projectName':projectName,
            'projectType':projectType,
            'userId':userId,
            'active':active,
            'creationDate':creationDate,
            'description':description
        }
    return response

def get_projects():
    #obtener los datos que tenemos en la db
    # users = mongo.db.users.find({'active':'true'})
    projects = mongo.db.projects.find()
    # convertir de bson a json
    response = json_util.dumps(projects)
    # el cliente lo vera como un string es por eso que necesitamos el mimetype 
    return Response(response, mimetype='application/json')

def filter_active_project(active):
    users = mongo.db.projects.find({'active':active})
    response = json_util.dumps(users)
    return Response(response, mimetype='application/json')

def filter_date_projects(key,values):
    if key[1]=='>':
        filter=mongo.db.projects.find({key[0]:{"$gte":(values)}})
    if key[1]=='<':
        filter=mongo.db.projects.find({key[0]:{"$lte": (values)}})     
    response = json_util.dumps(filter)
    return Response(response, mimetype='application/json')

def filter_active_date_projects(active,key,values):
    if key[1]=='>':
        filter=mongo.db.projects.find({"$and":[{"active":active},{key[0]:{"$gte": (values)}}]})
    if key[1]=='<':
        filter=mongo.db.projects.find({"$and":[{"active":active},{key[0]:{"$lte": (values)}}]})   
    response = json_util.dumps(filter)
    return Response(response, mimetype='application/json')

def get_project(id):
    #Con fine_one vamos a obtener unicamente el primer dato con el que haga match
    user = mongo.db.projects.find_one({'_id':ObjectId(id)}) #convertimos el id string a un ObjectId
    response = json_util.dumps(user)
    return Response(response, mimetype="application/json")

def delete_project(id):
    mongo.db.projects.delete_one({'_id': ObjectId(id)})
    response = jsonify({'message':'Project ' + id + ' was Deleted successfully'}) 
    return response

def update_project(id,projectName,projectType,userId,active,creationDate,description):
    mongo.db.projects.update_one({'_id':ObjectId(id)}, {'$set':{
        'projectName':projectName,
        'projectType':projectType,
        'userId':userId,
        'active':active,
        'creationDate':creationDate,
        'description':description
    }})
    response = jsonify({'message': 'Project ' + id + 'was update successfully'})
    return response

def get_user_project(id):
    user = mongo.db.projects.find({'userId':id})
    response = json_util.dumps(user)
    return Response(response, mimetype="application/json")
