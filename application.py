import os

from collections import deque

from flask import Flask, request, redirect, render_template, session
from flask_socketio import SocketIO, send, emit, join_room, leave_room

from login import login_required

from flask_avatars import Avatars

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
avatars = Avatars(app)
socketio = SocketIO(app)

users = []
channels = []
messages = {}

@app.route("/")
@login_required
def index():
    return render_template("dashboard.html", channels = channels)

@app.route("/login", methods = ['GET','POST'])
def login():
    session.clear()

    username = request.form.get("username")
    
    if request.method == "POST":
        if username in users:
            return render_template("login.html", channels = channels, alert = 1)                   
        if len(username) < 1 or username == '':
            return render_template("login.html", channels = channels, alert = 2)
        
        users.append(username)
        session['username'] = username
        session.permanent = True

        return redirect("/")
    
    else:
        return render_template("login.html")

@app.route("/logout", methods=['GET'])
def logout():
    try:
        users.remove(session['username'])
        session.clear()
    except:
        session.clear()

    return redirect("/")

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    new_channel = request.form.get("channel")

    if request.method == "POST":
        if new_channel in channels:
            return render_template("dashboard.html", channels = channels, alert = 3)
        
        channels.append(new_channel)
        messages[new_channel] = deque()

        return redirect("/channels/" + new_channel)
    
    else:
        return render_template("channel.html", channels = channels)

@app.route("/channels/<channel>", methods = ['GET', 'POST'])
@login_required
def my_channel(channel):
    session['current_channel'] = channel

    if request.method == "POST":       
        return redirect("/")
    
    try:
        return render_template("channel.html", channels = channels, messages = messages[channel])
    except:
        return redirect("/dashboard")

@socketio.on("joined", namespace='/')
def joined():
    room = session.get('current_channel')

    join_room(room)
    
    emit('status', {'userJoined': session['username'], 'channel': room, 'msg': session.get('username') + ' has entered the channel'}, room = room)

@socketio.on("left", namespace='/')
def left():
    room = session.get('current_channel')

    leave_room(room)

    emit('status', {'msg': session['username'] + ' has left the channel'}, room = room)

@socketio.on('send message')
def send_msg(msg, timestamp):
    room = session.get('current_channel')

    if len(messages[room]) > 100:
        messages[room].popleft()

    messages[room].append([timestamp, session.get('username'), msg])

    emit('announce message', {'user': session.get('username'), 'timestamp': timestamp, 'msg': msg}, room = room)

