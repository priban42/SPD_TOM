import time
from flask import Flask, request, jsonify, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import datetime
from utils import parse_svg_toilets
from pathlib import Path
import numpy as np

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
    tag_id = db.Column(db.Integer, nullable=False)
    stall_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)

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

def get_timestamps(node_id, stall_id):
    events = Event.query.filter_by(node_id=node_id, stall_id=stall_id).all()
    event_timestamps = np.zeros((len(events), 2), dtype=np.int64)
    for i in range(len(events)):
        event_timestamps[i, 0] = events[i].timestamp
        event_timestamps[i, 1] = events[i].event_type
    return event_timestamps

def compute_stats(timestamps):
    last_state = 1
    detected = False
    door_closed_ts = None
    visit_timestamps = []
    visit_durations = []
    for i in range(timestamps.shape[0]):
        state = timestamps[i, 1]
        if state == 1 and detected and last_state == 0:
            visit_timestamps.append(door_closed_ts)
            visit_durations.append(timestamps[i, 0] - door_closed_ts)
            detected = False
            door_closed_ts = None
            last_state = 1
        if state == 0:
            detected = False
            last_state = 0
            door_closed_ts = timestamps[i, 0]
        if state == 2:
            detected = True
    return np.array(visit_timestamps, dtype=np.int64), np.array(visit_durations, dtype=np.int64)

@app.route('/view')
def overview():
    floor_names = ["T2_1"]
    all_floors = []
    # timestamps = get_timestamps("T2_B3_1_0_M_3", 0)
    # stats = compute_stats(timestamps)
    for floor_name in floor_names:
        floor_path = 'static/' + floor_name + ".svg"
        all_floors.append({"svg_path":floor_path,
                           "toilets": parse_svg_toilets(floor_path)})
        for toilet in all_floors[-1]['toilets']:
            visits = 0
            visit_time = 0
            for stall_id in range(all_floors[-1]['toilets'][toilet]['stall_count']):
                timestamps = get_timestamps(toilet, stall_id)
                stats = compute_stats(timestamps)
                visits += len(stats[0])
                visit_time += np.sum(stats[1])
            all_floors[-1]['toilets'][toilet]['visits'] = visits
            all_floors[-1]['toilets'][toilet]['visit_time'] = visit_time

    pass
    return render_template('overview_template.html', all_floors=all_floors)

@app.route('/view/<string:toilet_name>/')
def toilet_view(toilet_name):
    timestamps = get_timestamps(toilet_name, 0)
    stats = compute_stats(timestamps)
    time_now = int(time.time())
    histogram, _ = np.histogram(stats[0], bins=(np.arange(0, 24 * 60 * 60, 60*60)+time_now - 23*60*60))
    labels = np.arange(0, 23, 1)-23
    return render_template(
        template_name_or_list='toilet_view_template.html',
        data=histogram.tolist(),
        labels=labels.tolist(),
        toilet_name=toilet_name
    )

# Run the server
if __name__ == '__main__':
    app.run(debug=DEBUG)
    # app.run(debug=DEBUG, host="0.0.0.0")  # use this to host on local network