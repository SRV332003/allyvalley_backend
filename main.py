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
socket = SocketIO(app)
CORS(app, resources={r"/*": {"origins": "*"}})

db = DB()
# db.reset(delete=True)
db.initialize()

@app.route("/")
def index():
    return jsonify({"status": "success"})

@app.post("/signup")
def signup():
    data = request.get_json()
    print(type(data))
    
    try:
        email = data["email"]
        name = data["name"]
        age = data["age"]
        gender = data['gender']
        language = data['language']
        about = data['about']
        profession = data['profession']
        phone = data['phone']
        interests = data['interests']
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": "Invalid data", "error": str(e)})

    user = db.query("Select * from users where email=%s", (email,))
    if user:
        return jsonify({"status": "error", "message": "User already exists"})


    db.query(
        "Insert into users (email,name,age,gender,languages,about,proffesion,phone) values (%s,%s,%s,%s,%s,%s,%s,%s)", 
        (email,name,age,gender,language,about,profession,phone)
    )
    
    for interest in interests:
        db.query("Insert into interests (interest_name,email) values (%s,%s)", (str(interest).lower(), email))


    return jsonify({"status": "success"})


@app.get("/getUser")
def getUser():
    email = request.args.get("email")

    user = db.query("Select * from users where email=%s", (email,))
    
    return jsonify({"status": "success", "user": user})

@app.post("/setStatus")
def setStatus():
    data = request.get_json()
    email = data["email"]
    status = data["status"]

    users = db.query("Select * from users where email=%s", (email,))
    if not users:
        return jsonify({"status": "error", "message": "User does not exist"})

    db.query("Update users set status=%s where email=%s", (status, email))

    return jsonify({"status": "success"})


@app.post("/getNearbyUsers")
def curLocation():
    results = []
    data = request.get_json()
    email = data["email"]
    lat = data["lat"]
    lon = data["lon"]
    print(email,lat,lon)

    users = db.query("Select * from users where email=%s", (email,))
    if not users:
        return jsonify({"status": "error", "message": "User does not exist"})

    db.query("Update users set lat=%s, lon=%s where status='true' and email=%s", (float(lat), float(lon), email))

    users = db.query("Select email,lat,lon from users where email!=%s", (email,))
    
    # print(users[0])

    
    
    for user in users:
        if geopy.distance.distance((lat, lon), (user["lat"], user['lon'])).m <= 25:
            results.append(user)

    return jsonify({"status": "success", "users": results})

@app.get("/getAllMessages")
def getAllMessages():
    email = request.args.get("email")
    receiver = request.args.get("receiver")

    messages = db.query("Select * from messages where (sender=%s and receiver=%s) or (sender=%s and receiver=%s) order by timestamp", (email, receiver, receiver, email))

    return jsonify({"status": "success", "messages": messages})

@app.post("/sendMessage")
def sendMessage():
    data = request.get_json()
    email = data["email"]
    receiver = data["receiver"]
    message = data["message"]

    try:
        users = db.query("Select * from users where email=%s", (email,))
        if not users:
            return jsonify({"status": "error", "message": "User does not exist"})

        users = db.query("Select * from users where email=%s", (receiver,))
        if not users:
            return jsonify({"status": "error", "message": "Receiver does not exist"})
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": "Invalid data", "error": str(e)})
    
    try:
        db.query("Insert into messages (sender,receiver,message) values (%s,%s,%s)", (email, receiver, message))
    except Exception as e: 
        print(e)
        return jsonify({"status": "error", "message": "Invalid data", "error": str(e)})

    return jsonify({"status": "success"})

@app.post("/sendRequest")
def sendRequest():
    data = request.get_json()
    email = data["email"]
    receiver = data["receiver"]

    db.query("Insert into matches (user1,user2) values (%s,%s)", (email, receiver))

    return jsonify({"status": "success"})

io = SocketIO(app, cors_allowed_origins="*")

userEmailDict = {}

@io.on("connection")
def handleConnect():

    print("Connected")
    
    @io.on("addUser")
    def handleAddUser(data):
        print(data)
        userEmailDict[data["email"]] = request.sid
        print(userEmailDict)

    @io.on("disconnect")
    def handleDisconnect():
        print("Disconnected")
        for email in userEmailDict:
            if userEmailDict[email] == request.sid:
                del userEmailDict[email]
                break

    @io.on("sendMessage")
    def handleRequest(data):
        print(data)
        sender = data["sender"]
        receiver = data["receiver"]
        message = data["message"]

        if receiver in userEmailDict:
            emit("recieveMessage", message,to=userEmailDict[receiver])




app.run(host='0.0.0.0')


