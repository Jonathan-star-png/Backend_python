from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash # nos permite recibir y cifrar las contraseñas, verificar las contraseñas
from bson import json_util #nos permite convertir del formato bson a json
from bson.objectid import ObjectId 
import json
from datetime import datetime
from services import userServices, projectServices
app = Flask(__name__)

@app.route('/users', methods=['POST'])
def create_user():
    # Recibimos datos
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    active = request.json['active']
    creationDate = request.json['creationDate']

    if username and email and password and active and creationDate:
        hashed_password=generate_password_hash(password)
        response=userServices.create_user(username,email,hashed_password,active,creationDate)
        return response
    else:
        return not_found()

@app.route('/users', methods=['GET'])
def get_users():
    arguments=request.args
    if arguments != {}:
        if 'active' in arguments and not('creationDate>' in arguments or 'creationDate<' in arguments):
            response=userServices.filter_active(arguments['active'])
            return response
        if ('creationDate>' in arguments or 'creationDate<' in arguments) and not('active' in arguments):
            for clave,val in arguments.items():
                response=slice_string(clave)
                result=userServices.filter_date(response,arguments[response[0]+response[1]])
            response=result
            return response
        if 'active' in arguments and ('creationDate>' in arguments or 'creationDate<' in arguments):
            if 'creationDate>' in arguments or 'creationDate<' in arguments:
                for clave,val in arguments.items():
                    if clave == 'creationDate>' or clave == 'creationDate<':
                        response=slice_string(clave)
                        result=userServices.filter_active_date(arguments['active'],response,arguments[response[0]+response[1]])
                        response=result
                        return response     
    else:
        response = userServices.get_users()
        return response

def slice_string(my_str):
    my_string=str(my_str)
    symbol = my_string[-1]
    key = my_string[:-1]
    response = [key,symbol]
    return response


@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    response = userServices.get_user(id)
    return response
   
@app.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    response = userServices.delete_user(id)
    return response

@app.route('/users/<id>', methods=['PUT'])
def update_user(id):
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    active = request.json['active']
    creationDate = request.json['creationDate']
    
    if username and email and password and active and creationDate:
        hashed_password=generate_password_hash(password)
        response = userServices.update_user(id,username,hashed_password,email,active,creationDate)
        return response
    else:
        return not_found()


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
        response=projectServices.create_project(projectName,projectType,userId,active,creationDate,description)
        return response
    else:
        return not_found()

@app.route('/projects', methods=['GET'])
def get_projects():
    arguments=request.args
    if arguments != {}:
        if 'active' in arguments and not('creationDate>' in arguments or 'creationDate<' in arguments):
            response=projectServices.filter_active_project(arguments['active'])
            return response
        if ('creationDate>' in arguments or 'creationDate<' in arguments) and not('active' in arguments):
            for clave,val in arguments.items():
                response=slice_string_projects(clave)
                result=projectServices.filter_date_projects(response,arguments[response[0]+response[1]])
            response=result
            return response
        if 'active' in arguments and ('creationDate>' in arguments or 'creationDate<' in arguments):
            if 'creationDate>' in arguments or 'creationDate<' in arguments:
                for clave,val in arguments.items():
                    if clave == 'creationDate>' or clave == 'creationDate<':
                        response=slice_string_projects(clave)
                        result=projectServices.filter_active_date_projects(arguments['active'],response,arguments[response[0]+response[1]])
                        response=result
                        return response  
        # return 'Hola'   
    else:
        response = projectServices.get_projects()
        return response


def slice_string_projects(my_str):
    my_string=str(my_str)
    symbol = my_string[-1]
    key = my_string[:-1]
    response = [key,symbol]
    return response


@app.route('/projects/<id>', methods=['GET'])
def get_project(id):
    response = projectServices.get_project(id)
    return response
   
@app.route('/projects/<id>', methods=['DELETE'])
def delete_project(id):
    response = projectServices.delete_project(id)
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
        response = projectServices.update_project(id,projectName,projectType,userId,active,creationDate,description)
        return response
    else:
        return not_found()

@app.route('/users/<id>/projects', methods=['GET'])
def get_user_project(id):
    response = projectServices.get_user_project(id)
    return response


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
