import os

from collections import deque

from flask import Flask, render_template, session, request, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room

from helpers import login_required

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
    return render_template("index.html", channels = channels)

@app.route("/signin", methods=['GET','POST'])
def signin():
    session.clear()

    username = request.form.get("username")
    
    if request.method == "POST":
        if len(username) < 1 or username == '':
            return "username can't be empty"
        if username in users:
            return "that username already exists!"                    
        
        users.append(username)
        session['username'] = username
        session.permanent = True

        return redirect("/")
    
    else:
        return render_template("signin.html")

@app.route("/logout", methods=['GET'])
def logout():
    try:
        users.remove(session['username'])
        session.clear()
    except:
        session.clear()

    return redirect("/")

@app.route("/create", methods=['GET','POST'])
def create():
    newChannel = request.form.get("channel")

    if request.method == "POST":
        if newChannel in channels:
            return "that channel already exists!"
        
        channels.append(newChannel)
        messages[newChannel] = deque()

        return redirect("/channels/" + newChannel)
    
    else:
        return render_template("channel.html", channels = channels)

@app.route("/channels/<channel>", methods=['GET','POST'])
@login_required
def enter_channel(channel):
    session['current_channel'] = channel

    if request.method == "POST":       
        return redirect("/")
    
    try:
        return render_template("channel.html", channels= channels, messages=messages[channel])
    except:
        return redirect("/create")

@socketio.on("joined", namespace='/')
def joined():
    room = session.get('current_channel')

    join_room(room)
    
    emit('status', {'userJoined': session.get('username'), 'channel': room, 'msg': session.get('username') + ' has entered the channel'}, room = room)

@socketio.on("left", namespace='/')
def left():
    room = session.get('current_channel')

    leave_room(room)

    emit('status', {'msg': session.get('username') + ' has left the channel'}, room = room)

@socketio.on('send message')
def send_msg(msg, timestamp):
    room = session.get('current_channel')

    if len(messages[room]) > 100:
        messages[room].popleft()

    messages[room].append([timestamp, session.get('username'), msg])

    emit('announce message', {'user': session.get('username'), 'timestamp': timestamp, 'msg': msg}, room = room)

