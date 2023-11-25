from flask import *
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit
from flask_ngrok import run_with_ngrok
from db import DB
import geopy.distance
import json
import psycopg2


app = Flask(__name__)
run_with_ngrok(app)
CORS(app, resources={r"/*": {"origins": "*"}})

db = DB()

@app.post("/signup")
def signup():
    data = request.get_json()
    
    email = data["email"]
    interests = data["interests"]
    age = data["age"]
    gender = data['gender']
    language = data['language']
    about = data['about']
    proffesion = data['proffesion']
    phone = data['phone']

    db.query(
        "Insert into users (email,interests,age,gender,languages,about,proffesion,phone) values (%s,%s,%s,%s,%s,%s,%s,%s)", 
        (email,interests,age,gender,language,about,proffesion,phone)
    )
    
    return jsonify({"status": "success"})

