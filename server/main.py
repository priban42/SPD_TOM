import time
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import datetime

from server.utils import heatmap_color, get_histogram
from utils import parse_svg_toilets, heatmap_color, get_time_labels
from pathlib import Path
import numpy as np
from structures import *
import os

app = Flask(__name__)

DEBUG = True

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'mysecret'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
admin = Admin(app, name="Admin Dashboard", template_mode="bootstrap3")
# login_manager = LoginManager(app)
EVENT_TYPES = ["door_closed", "door_opened", "PIR", "RFID"]

# Database models
class Node(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('node.id'), nullable=False)
    event_type = db.Column(db.Integer, nullable=False)
    tag_id = db.Column(db.String(32), nullable=False)
    stall_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)

buildings = {"T2":Building("T2", Event),
             "KN":Building("KN", Event)}


# Create tables
with app.app_context():
    db.create_all()

class NodeModelView(ModelView):
    column_list = ['id', 'node_id', 'password']
    column_searchable_list = ['node_id']
    column_sortable_list = ['node_id']
    def on_model_change(self, form, model, is_created):
        # Hash password when creating or updating a user
        if is_created:
            model.set_password(form.password.data)
        else:
            if form.password.data:
                model.set_password(form.password.data)
        return super(NodeModelView, self).on_model_change(form, model, is_created)

    def is_accessible(self):
        return True

class EventModelView(ModelView):
    column_list = ['id', 'node_id', 'event_type', 'tag_id', 'stall_id', 'timestamp']
    column_searchable_list = ['node_id', 'event_type', 'tag_id']
    column_sortable_list = ['node_id', 'event_type', 'tag_id']
    def is_accessible(self):
        return True

if DEBUG:
    admin.add_view(NodeModelView(Node, db.session))
    admin.add_view(EventModelView(Event, db.session))


# db.session.add(Node(node_id='username', password=bcrypt.generate_password_hash('password').decode('utf-8')))
# db.session.commit()

# Store Data (Protected)
@app.route('/data', methods=['POST'])
def store_data():
    data = request.get_json()
    current_node = Node.query.filter_by(node_id=data['node_id']).first()
    if current_node and current_node.check_password(data['password']):
        current_time = int(time.time())
        if not (len(data["timestamps"]) == len(data["event_types"]) == len(data["tag_ids"]) == len(data["stall_ids"])):
            return jsonify({"message": "Invalid data"}), 401
        for i in range(len(data["timestamps"])):
            new_entry = Event(node_id=data['node_id'],
                             timestamp=current_time + data["timestamps"][i] - data["elapsed_time"],
                             event_type=data["event_types"][i],
                             tag_id=data["tag_ids"][i],
                             stall_id=data["stall_ids"][i]
                             )
            db.session.add(new_entry)
        db.session.commit()
        return jsonify({"message": "Data stored successfully"}), 201
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/')
def title():
    return render_template('title.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/building_view/<string:building_name>')
def overview(building_name):
    building = buildings[building_name]
    building.refresh_data()
    return render_template('overview_template.html', building=building, color_mapping=heatmap_color)

@app.route('/toilet_view/<string:toilet_name>/<string:interval>')
def toilet_view(toilet_name, interval):
    if interval not in ["day", "week", "month", "year"]:
        return redirect(url_for('toilet_view', toilet_name=toilet_name, interval="day"))
    building_name = toilet_name.split("_")[0]
    building = buildings[building_name]
    floor_name = building_name + "_" + toilet_name.split("_")[2]
    toilet = building[floor_name][toilet_name]
    toilet.parent.refresh_data()
    # toilet.refresh_data()
    time_now = int(time.time())
    histogram, _ = np.histogram(toilet.visit_timestamps, bins=(np.arange(0, 24 * 60 * 60, 60*60)+time_now - 23*60*60))
    labels = np.arange(0, 23, 1)-23
    labels = get_time_labels("day")
    bagr = get_time_labels("week")
    return render_template(
        template_name_or_list='toilet_view_template.html',
        get_histogram=get_histogram,
        get_time_labels=get_time_labels,
        interval=interval,
        # data=histogram.tolist(),
        # labels=labels,
        toilet=toilet,
        scale=20,
        color_mapping=heatmap_color
    )


# Run the server
if __name__ == '__main__':

    # app.run(debug=DEBUG)
    app.run(debug=DEBUG, host="0.0.0.0")  # use this to host on local network
    for key in buildings:
        buildings[key].refresh_data()
