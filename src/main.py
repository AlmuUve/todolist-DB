"""
This module takes care of starting the API Server, 
Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Task
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user/<user_name>', methods=['GET'])
def get_one_user(user_name):
    name = User.get_by_name(user_name)
    try:
        return jsonify(name.serialize()), 200
    except: 
        return name, 400

@app.route('/user', methods=['POST'])
def create_user():
    body = request.get_json()
    if body.get("user_name", None):
        new_user = User(name = body.get("user_name"), is_active = True)
        new_user.add()
        return jsonify(new_user.serialize()), 200
    return "", 400

@app.route('/user/<user_name>', methods=['DELETE'])
def delete_one_user(user_name):
    User.delete_user(user_name)
    return "user deleted coñññño",200


@app.route('/user/<user_name>/tasks', methods=['GET'])
def get_user_tasks(user_name):
    user = User.get_by_name(user_name).serialize()
    tasks = Task.get_by_user(user.get('id'))
    tasks_list = [task.serialize() for task in tasks if tasks is not None]
    return jsonify(tasks_list), 200

@app.route('/user/<user_name>/tasks', methods=['POST'])
def add_user_new_task(user_name):
    user = User.get_by_name(user_name).serialize()
    new_tasks = request.get_json()
    for new_task in new_tasks:
        task = Task(
            label= new_task.get('label'),
            is_done= new_task.get('is_done'),
            user_id=user.get('id')
        )
        print(task)
        task.add()
    return "Added tasks", 200

@app.route('/user/<user_name>/tasks/<id>', methods=['PUT'])
def update_task(user_name, id):
    
        body=request.get_json()
        id=int(id)
        #get de la tarea
        Task.update(id, body['label'], body['is_done'])#use get
        return "okay", 200 #get de 1 tarea

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
