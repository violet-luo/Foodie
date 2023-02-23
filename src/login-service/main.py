import hashlib
from flask import request, Flask, Response
from flask_login import LoginManager, login_user, logout_user, UserMixin
from dotenv import load_dotenv
import os
import pymongo

app = Flask(__name__)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

app.secret_key = os.environ.get('SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_json):
        self.user_json = user_json

    def get_id(self):
        object_id = self.user_json.get('_id')
        return str(object_id)

def mongoConnection():
    try:
        client = pymongo.MongoClient(os.environ.get('MONGO_DB_CLUSTER'))
        print('Successfully connected to Mongo DB!')
        db = client["restaurant_db"]
        col = db["users"]
        return col
    except:
        return Exception("Failed to connect to mongo db")

@app.route('/register', methods=['GET', 'POST'])
def register_account():
    try:
        col = mongoConnection()
    except:
        return Response(status=400)
    data = request.get_json()
    email = data['email']
    password = data['password']
    hashed_pwd = hashlib.md5(password.encode()).hexdigest()
    user_json = {
        "email": email,
        "hashed_pwd": hashed_pwd
    }
    added_record = col.insert_one(user_json)
    return {'id': str(added_record.inserted_id)}, 200

@app.route('/login', methods=['POST'])
def login():
    try:
        col = mongoConnection()
    except:
        return Response(status=400)
    data = request.get_json()
    email = data['email']
    password = data['password']
    hashed_pwd = hashlib.md5(password.encode()).hexdigest()
    user_json = col.find_one({"email": email, "hashed_pwd": hashed_pwd})
    if user_json:
        user = User(user_json)
        login_user(user)
        return {'id': str(user.user_json["_id"])}, 200
    else:
        return {'error': 'login failed'}, 400

@app.route('/logout')
def logout():
    logout_user()
    return {'msg': 'user logged out'}, 200

@login_manager.user_loader
def user_loader(user_id):
    try:
        col = mongoConnection()
    except:
        return Response(status=400)
    user_json = col.find_one({"_id": user_id})
    return User(user_json)

if __name__ == '__main__':
    app.run(host='0.0.0.0')