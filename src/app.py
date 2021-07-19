from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash # nos permite recibir y cifrar las contraseñas, verificar las contraseñas
from bson import json_util #nos permite convertir del formato bson a json
from bson.objectid import ObjectId 

app = Flask(__name__)
app.config['MONGO_URI']='mongodb://localhost/pythonmongodb'#conexion a mongodb
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
    active=request.args
    print(active)
    #obtener los datos que tenemos en la db
    # users = mongo.db.users.find({'active':'true'})
    users = mongo.db.users.find()
    # convertir de bson a json
    response = json_util.dumps(users)
    # el cliente lo vera como un string es por eso que necesitamos el mimetype 
    return Response(response, mimetype='application/json')

@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    #Con fine_one vamos a obtener unicamente el primer dato con el que haga match
    user = mongo.db.users.find_one({'_id':ObjectId(id)}) #convertimos el id string a un ObjectId
    response = json_util.dumps(user)
    return Response(response, mimetype="application/json")
   

@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    mongo.db.users.delete_one({'_id': ObjectId(id)})
    response = jsonify({'message':'User ' + id + ' was Deleted successfully'}) 
    return response

@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    
    if username and email and password:
        hashed_password=generate_password_hash(password)
        mongo.db.users.update_one({'_id':ObjectId(id)}, {'$set':{
            'username':username,
            'password':hashed_password,
            'email':email
        }})
        response = jsonify({'message': 'User ' + id + 'was update successfully'})
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
