from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash # nos permite recibir y cifrar las contraseñas, verificar las contraseñas
from bson import json_util #nos permite convertir del formato bson a json
from bson.objectid import ObjectId 
import json
from datetime import datetime
app = Flask(__name__)
# app.config['MONGO_URI']='mongodb://localhost/pythonmongodb'#conexion a mongodb
app.config['MONGO_URI']='mongodb://172.19.0.1:27017/pythonmongodb'
mongo = PyMongo(app)#variable para acceder a mongodb

@app.route('/users', methods=['POST'])
def create_user():
    # Recibimos datos
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    active = request.json['active']
    creationDate = request.json['creationDate']

    if username and email and password and active and creationDate:
        #ciframos la contraseña de los usuarios
        hashed_password=generate_password_hash(password)
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
    else:
        return not_found()

    return {'message': 'received'}

@app.route('/users', methods=['GET'])
def get_users():
    arguments=request.args
    if arguments != {}:
        if 'active' in arguments and not('creationDate>' in arguments or 'creationDate<' in arguments):
            response=filter_active(arguments['active'])
            return response
        if ('creationDate>' in arguments or 'creationDate<' in arguments) and not('active' in arguments):
            for clave,val in arguments.items():
                response=slice_string(clave)
                result=filter_date(response,arguments[response[0]+response[1]])
            response=result
            return response
        if 'active' in arguments and ('creationDate>' in arguments or 'creationDate<' in arguments):
            if 'creationDate>' in arguments or 'creationDate<' in arguments:
                for clave,val in arguments.items():
                    if clave == 'creationDate>' or clave == 'creationDate<':
                        response=slice_string(clave)
                        result=filter_active_date(arguments['active'],response,arguments[response[0]+response[1]])
                        response=result
                        return response     
    else:
        #obtener los datos que tenemos en la db
        # users = mongo.db.users.find({'active':'true'})
        users = mongo.db.users.find()
        # convertir de bson a json
        response = json_util.dumps(users)
        # el cliente lo vera como un string es por eso que necesitamos el mimetype 
        return Response(response, mimetype='application/json')
        # return response

def filter_active(active):
    users = mongo.db.users.find({'active':active})
    response = json_util.dumps(users)
    return Response(response, mimetype='application/json')

def slice_string(my_str):
    my_string=str(my_str)
    symbol = my_string[-1]
    key = my_string[:-1]
    response = [key,symbol]
    return response

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

@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    #Con fine_one vamos a obtener unicamente el primer dato con el que haga match
    user = mongo.db.users.find_one({'_id':ObjectId(id)}) #convertimos el id string a un ObjectId
    response = json_util.dumps(user)
    return Response(response, mimetype="application/json")
   
@app.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    mongo.db.users.delete_one({'_id': ObjectId(id)})
    response = jsonify({'message':'User ' + id + ' was Deleted successfully'}) 
    return response

@app.route('/users/<id>', methods=['PUT'])
def update_user(id):
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    active = request.json['active']
    creationDate = request.json['creationDate']
    
    if username and email and password:
        hashed_password=generate_password_hash(password)
        mongo.db.users.update_one({'_id':ObjectId(id)}, {'$set':{
            'username':username,
            'password':hashed_password,
            'email':email,
            'active':active,
            'creationDate':creationDate
        }})
        response = jsonify({'message': 'User ' + id + 'was update successfully'})
        return response
    else:
        return not_found()
    return {'message': 'received'}

@app.route('/users/<id>/projects', methods=['GET'])
def get_user_project(id):
    user = mongo.db.projects.find({'userId':id})
    response = json_util.dumps(user)
    return Response(response, mimetype="application/json")


@app.route('/projects', methods=['POST'])
def project():
    # Recibimos datos
    projectName = request.json['projectName']
    projectType = request.json['projectType']
    userId = request.json['userId']
    active = request.json['active']
    creationDate = request.json['creationDate']
    description = request.json['description']

    if projectName and projectType and userId and active and creationDate and description:
        #insertamos en la colección
        id = mongo.db.projects.insert(
            {'projectName':projectName, 'projectType':projectType, 'userId':userId,'active':active,'creationDate':creationDate,'description':description}
        )

        #respuesta cuando creamos el usuario
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
    else:
        return not_found()

    return {'message': 'received'}

@app.route('/projects', methods=['GET'])
def get_projects():
    arguments=request.args
    if arguments != {}:
        if 'active' in arguments and not('creationDate>' in arguments or 'creationDate<' in arguments):
            response=filter_active_project(arguments['active'])
            return response
        if ('creationDate>' in arguments or 'creationDate<' in arguments) and not('active' in arguments):
            for clave,val in arguments.items():
                response=slice_string_projects(clave)
                result=filter_date_projects(response,arguments[response[0]+response[1]])
            response=result
            return response
        if 'active' in arguments and ('creationDate>' in arguments or 'creationDate<' in arguments):
            if 'creationDate>' in arguments or 'creationDate<' in arguments:
                for clave,val in arguments.items():
                    if clave == 'creationDate>' or clave == 'creationDate<':
                        response=slice_string_projects(clave)
                        result=filter_active_date_projects(arguments['active'],response,arguments[response[0]+response[1]])
                        response=result
                        return response  
        # return 'Hola'   
    else:
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

def slice_string_projects(my_str):
    my_string=str(my_str)
    symbol = my_string[-1]
    key = my_string[:-1]
    response = [key,symbol]
    return response

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

@app.route('/projects/<id>', methods=['GET'])
def get_project(id):
    #Con fine_one vamos a obtener unicamente el primer dato con el que haga match
    user = mongo.db.projects.find_one({'_id':ObjectId(id)}) #convertimos el id string a un ObjectId
    response = json_util.dumps(user)
    return Response(response, mimetype="application/json")
   
@app.route('/projects/<id>', methods=['DELETE'])
def delete_project(id):
    mongo.db.projects.delete_one({'_id': ObjectId(id)})
    response = jsonify({'message':'Project ' + id + ' was Deleted successfully'}) 
    return response

@app.route('/projects/<id>', methods=['PUT'])
def update_project(id):
    projectName = request.json['projectName']
    projectType = request.json['projectType']
    userId = request.json['userId']
    active = request.json['active']
    creationDate = request.json['creationDate']
    description = request.json['description']
    
    if projectName and projectType and userId and active and creationDate and description:
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
    else:
        return not_found()
    return {'message': 'received'}




@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'message': 'Resource Not Foud: ' + request.url,
        'status': 404
    })
    response.status_code = 404 #el código de estado 
    return response #es la respuesta

if __name__=="__main__":
    app.run(debug=True)
