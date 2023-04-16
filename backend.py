import os
from flask import Flask, request, jsonify, send_from_directory, make_response, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.utils import secure_filename
from sqlalchemy import Interval, Numeric
from datetime import timedelta
from flask_login import UserMixin, login_user, LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import hashlib

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Iamsuperman:devxspace@Iamsuperman.mysql.pythonanywhere-services.com/Iamsuperman$devxspace'

# login = LoginManager(app)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.secret_key = os.urandom(24)

db = SQLAlchemy(app)
migrate = Migrate(app, db)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(42), nullable=False, unique=True)
    avatar = db.Column(db.String(255), nullable=True)
    username = db.Column(db.String(20), nullable=True, unique=True)
    about = db.Column(db.String(1000), nullable=True)
    skills = db.relationship('Skill', backref='user', lazy=True)

    services = db.relationship('Service', backref='user', lazy=True, foreign_keys='Service.user_address')

    def __repr__(self):
        return f"User {self.address}"



class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(20), nullable=True)
    user_address = db.Column(db.String(42), db.ForeignKey('user.address'), nullable=False)


    def __repr__(self):
        return f"Name: {self.name}, Image: {self.image_file}"

class Agent(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(42), nullable=False, unique=True)
    avatar = db.Column(db.String(255), nullable=True)
    username = db.Column(db.String(20), nullable=True, unique=True)
    password = db.Column(db.String(255), nullable=True)
    superAgent = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Address: {self.address}, Name: {self.username}"

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(Numeric(18, 6))
    finalized = db.Column(db.Boolean, default=False)
    accepted = db.Column(db.Boolean, default=False)
    completed = db.Column(db.Boolean, default=False)
    rejected = db.Column(db.Boolean, default=False)
    paid = db.Column(db.Boolean, default=False)
    abort = db.Column(db.Boolean, default=False)
    canceled = db.Column(db.Boolean, default=False)
    ongoing = db.Column(db.Boolean, default=False)
    deadline = db.Column(Interval)
    agent_address = db.Column(db.String(42), db.ForeignKey('agent.address'))
    developer_address = db.Column(db.String(42), nullable=False)
    buyer_address = db.Column(db.String(42), db.ForeignKey('user.address'), nullable=False)

    @property
    def status(self):
        if self.accepted:
            return "accepted"
        elif self.rejected:
            return "rejected"
        elif self.completed:
            return "completed"
        elif self.ongoing:
            return "ongoing"
        elif self.buyer_finalized:
            return "finalized"
        else:
            return "pending"

    def __repr__(self):
        return f"Task {self.id}, Title: {self.title}, Status: {self.status}"


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"Task {self.id}, Title: {self.name}, user_id: {self.user_id}"




class AgentView(ModelView):
    column_display_pk = True
    can_create = True
    can_edit = True
    can_delete = True

class UserView(ModelView):
    column_display_pk = True
    can_create = True
    can_edit = True
    can_delete = True

class ServiceView(ModelView):
    column_display_pk = True
    can_create = True
    can_edit = True
    can_delete = True

class TaskView(ModelView):
    column_display_pk = True
    can_create = True
    can_edit = True
    can_delete = True

class SkillView(ModelView):
    column_display_pk = True
    can_create = True
    can_edit = True
    can_delete = True

# Add the views to the admin object
admin = Admin(app, name='Admin Panel')
admin.add_view(UserView(User, db.session))
admin.add_view(ServiceView(Service, db.session))
admin.add_view(TaskView(Task, db.session))
admin.add_view(SkillView(Skill, db.session))
admin.add_view(AgentView(Agent, db.session))



# def admin_():
#     if request.method == 'POST':
#         address = request.form.get('address')
#         if address:
#             user = Agent.query.filter_by(address=address).first()
#         if user and user.superAgent:
#             admin = Admin(app, name='My App')
#             # Allow access to admin page
#             admin.add_view(UserView(User, db.session))
#             admin.add_view(ServiceView(Service, db.session))
#             admin.add_view(TaskView(Task, db.session))
#             admin.add_view(SkillView(Skill, db.session))
#             admin.add_view(AgentView(Agent, db.session))
#             return admin.render('admin.html')
#         else:
#             return "Not authorized", 404
#     else:
#         response = make_response("<html><body><form action='/admin' method='POST'><label for='address'>Address:</label><input type='text' id='address' name='address'><br><input type='submit' value='Submit'></form></body></html>")
#         return response

# @app.route('/admin_', methods=['GET', 'POST'])
# def admin_route():
#     return admin_()



@app.route('/create_profile', methods=['POST'])
def create_profile():
    username = request.form.get('username')
    about = request.form.get('about')
    skill_names = request.form.getlist('skills')
    address = request.form.get('address')
    avatar = request.files.get('avatar')

    user = User.query.filter_by(address=address).first()

    if user:
        return jsonify({'error': 'address already exists'}), 409

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409

    if not avatar:
        return jsonify({'error': 'avatar not present'}), 401

    filename = None
    if avatar:
        filename = secure_filename(avatar.filename)
        avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        avatar.save(avatar_path)
        avatar_url = f'/uploads/{filename}'

    user = User(address=address, avatar=avatar_url, username=username, about=about)
    db.session.add(user)
    db.session.commit()

    skills = []
    for skill_name in skill_names:
        skill = Skill(name=skill_name, user=user)
        db.session.add(skill)
        db.session.commit()
        skills.append(skill.name)

    return jsonify({'success': 'Profile created successfully', 'skills': skills, 'avatar': avatar_url})



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/users')
def get_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_dict = {
            'id': user.id,
            'address': user.address,
            'avatar': user.avatar,
            'username': user.username,
            'about': user.about,
            'skills': [skill.name for skill in user.skills]
        }
        user_list.append(user_dict)
    return {'users': user_list}


@app.route('/users/<address>')
def get_user(address):
    user = User.query.filter_by(address=address).first()
    if user:
        return {
            'id': user.id,
            'address': user.address,
            'avatar': user.avatar,
            'username': user.username,
            'about': user.about,
            'skills': [skill.name for skill in user.skills]
        }
    else:
        return {'error': f'User with address {address} not found'}, 404




# UPDATE A USER PROFILE

@app.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.json

    user_address = data.get('user_address')
    user = User.query.filter_by(address=user_address).first()
    if not user:
        return jsonify({'message': 'User not found.'}), 404

    avatar = data.get('avatar')
    username = data.get('username')
    about = data.get('about')
    skills = data.get('skills')

    if avatar:
        user.avatar = avatar
    if username:
        user.username = username
    if about:
        user.about = about
    if skills:
        # First remove all existing skills
        for skill in user.skills:
            db.session.delete(skill)
        # Then add new skills
        for skill_name in skills:
            skill = Skill(name=skill_name, user=user)
            db.session.add(skill)

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully.'}), 200



# REGISTER A SERVICE AS A FREELANCER
@app.route('/register_service', methods=['POST'])
def register_service():
    address = request.form.get('address')
    user = User.query.filter_by(address=address).first()
    if not user:
        return jsonify({'message': 'user not found'}), 401

    service_name = request.form.get('service_name')
    service_desc = request.form.get('service_desc')
    service_image = request.files.get('service_image')

    if not service_desc:
        return jsonify({'message': 'empty description'}), 401

    if not service_image:
        return jsonify({'message': 'empty image'}), 401

    filename = None
    if service_image:
        filename = secure_filename(service_image.filename)
        service_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        service_image.save(service_image_path)
        service_image_url = f'/uploads/{filename}'

    new_service = Service(name=service_name, description=service_desc, image_file=service_image_url, user=user)
    db.session.add(new_service)
    db.session.commit()

    return jsonify({'message': 'Service registered successfully.', 'image_url': service_image_url}), 200







@app.route('/hire_developer', methods=['POST'])
def hire_developer():
    data = request.get_json()
    # task_id = data.get('task_id')
    buyer_address = data.get('buyer_address')
    user = User.query.filter_by(address=buyer_address).first()

    title = data.get('title')
    description = data.get('description')
    time_frame_days = int(data.get('time_frame'))
    time_frame = timedelta(days=time_frame_days)
    price = data.get('price')
    developer_address = data.get('developer_address')
    if not user:
        return jsonify({'message': 'you need to create a profile for this'}), 401

    if not title:
        return jsonify({'message': 'add a title'}), 401

    if not buyer_address:
        return jsonify({'message': 'please connect your wallet'}), 401

    if not description:
        return jsonify({'message': 'add a description'}), 401

    if not time_frame_days:
        return jsonify({'message': 'add a duration'}), 401

    if not price:
        return jsonify({'message': 'add a price'}), 401
    # if not task_id:
    #     return jsonify({'message': 'add a fucking task_id, and stop crashing my server'}), 401

    if not developer_address:
        return jsonify({'message': 'gettat abeg'}), 401


    task = Task(title=title, description=description, price=price, deadline=time_frame, buyer_address=buyer_address, developer_address=developer_address)
    db.session.add(task)
    db.session.commit()

    return jsonify({'message': 'Task created successfully.'}), 200


# LIST OF TASKS AVAILABLE TO A DEVELOPER
@app.route('/available_tasks/<address>', methods=['GET'])
def get_available_tasks(address):
    # Check if user exists
    user = User.query.filter_by(address=address).first()
    if not user:
        return jsonify({'message': 'user not found'}), 401

    # Get available tasks for developer
    available_tasks = Task.query.filter_by(developer_address=address, accepted=False, rejected=False, completed=False, ongoing=False).all()

    tasks = []
    for task in available_tasks:
        # Query User table to get username of buyer_address
        buyer = User.query.filter_by(address=task.buyer_address).first()
        tasks.append({
            'id': task.task_id,
            'title': task.title,
            'description': task.description,
            'price': task.price,
            'accepted': task.accepted,
            'completed': task.completed,
            'ongoing': task.ongoing,
            'rejected': task.rejected,
            'deadline': task.deadline.total_seconds(),
            'developer_address': task.developer_address,
            'buyer_address': task.buyer_address,
            'buyer_username': buyer.username
        })

    return jsonify({'tasks': tasks}), 200

# get tasks that has been accepted for the developer
@app.route('/ongoing_tasks/<address>', methods=['GET'])
def get_ongoing_tasks(address):
    # Check if user exists
    user = User.query.filter_by(address=address).first()
    if not user:
        return jsonify({'message': 'user not found'}), 401

    # Get available tasks for developer
    ongoing_tasks = Task.query.filter_by(developer_address=address, paid=True, abort=False, accepted=True, rejected=False, finalized=False, ongoing=True).all()

    tasks = []
    for task in ongoing_tasks:
        # Query User table to get username of buyer_address
        buyer = User.query.filter_by(address=task.buyer_address).first()
        tasks.append({
            'task_id': task.task_id,
            'title': task.title,
            'description': task.description,
            'price': task.price,
            'developer_address': task.developer_address,
            'completed': task.completed,
            'ongoing': task.ongoing,
            'rejected': task.rejected,
            'deadline': task.deadline.total_seconds(),
            'buyer_address': task.buyer_address,
            'buyer_username': buyer.username
        })

    return jsonify({'tasks': tasks}), 200


# get the accepted tasks in progress for the buyer
@app.route('/tasks_accepted/<address>', methods=['GET'])
def get_accepted_tasks(address):
    # Check if user exists
    user = User.query.filter_by(address=address).first()
    if not user:
        return jsonify({'message': 'user not found'}), 401

    # Get available tasks for developer
    ongoing_tasks = Task.query.filter_by(buyer_address=address, abort=False, paid=True, accepted=True, finalized=False, rejected=False, ongoing=True).all()

    tasks = []
    for task in ongoing_tasks:
        # Query User table to get username of buyer_address
        developer = User.query.filter_by(address=task.developer_address).first()
        tasks.append({
            'task_id': task.task_id,
            'title': task.title,
            'description': task.description,
            'price': task.price,
            'developer_address': task.developer_address,
            'completed': task.completed,
            'ongoing': task.ongoing,
            'rejected': task.rejected,
            'deadline': task.deadline.total_seconds(),
            'buyer_address': task.buyer_address,
            'buyer_username': developer.username
        })

    return jsonify({'tasks': tasks}), 200



# get all the accepted tasks a buyer can pay for
@app.route('/payable/<address>', methods=['GET'])
def get_all_tasks(address):
    # Check if user exists
    user = User.query.filter_by(address=address).first()
    if not user:
        return jsonify({'message': 'user not found'}), 401

    # Get available tasks for developer
    ongoing_tasks = Task.query.filter_by(buyer_address=address, rejected=False, canceled=False, paid=False).all()

    tasks = []
    for task in ongoing_tasks:
        # Query User table to get username of buyer_address
        developer = User.query.filter_by(address=task.developer_address).first()
        tasks.append({
            'task_id': task.task_id,
            'title': task.title,
            'description': task.description,
            'price': task.price,
            'developer_address': task.developer_address,
            'completed': task.completed,
            'ongoing': task.ongoing,
            'rejected': task.rejected,
            'canceled': task.canceled,
            'paid': task.paid,
            'accepted': task.accepted,
            'deadline': task.deadline.total_seconds(),
            'buyer_address': task.buyer_address,
            'buyer_username': developer.username
        })

    return jsonify({'tasks': tasks}), 200


# GET CLIENT'S TASKS  IN PROGRESS
@app.route('/tasks_in_progress/<address>', methods=['GET'])
def client_ongoing_tasks(address):
    # Check if user exists
    user = User.query.filter_by(address=address).first()
    if not user:
        return jsonify({'message': 'user not found'}), 401

    # Get available tasks for client
    ongoing_tasks = Task.query.filter_by(buyer_address=address, paid=True, accepted=True, rejected=False, completed=False, ongoing=True).all()

    tasks = []
    for task in ongoing_tasks:
        # Query User table to get username of buyer_address
        developer = User.query.filter_by(address=task.developer_address).first()
        tasks.append({
            'task_id': task.task_id,
            'title': task.title,
            'description': task.description,
            'price': task.price,
            'developer_address': task.developer_address,
            'completed': task.completed,
            'ongoing': task.ongoing,
            'accepted': task.accepted,
            'rejected': task.rejected,
            'deadline': task.deadline.total_seconds(),
            'buyer_address': task.buyer_address,
            'developer_username': developer.username
        })

    return jsonify({'tasks': tasks}), 200


# finalize task
@app.route('/finalize', methods=['POST'])
def finalize():
    data = request.get_json()
    task_id = data.get('task_id')
    buyer_address = data.get('address')
    finalize_status = data.get('status')
    print(data)

    if not task_id:
        return jsonify({'message': 'task id unavailable'}), 401

    if not buyer_address:
        return jsonify({'message': 'buyer address unavailable'}), 401

    task = Task.query.filter_by(task_id=task_id, buyer_address=buyer_address, completed=True, accepted=True, rejected=False).first()

    if not task:
        return jsonify({'message': 'task not available'}), 400

    if finalize_status == 1:
        task.finalized = True
    else:
        task.completed = False
        task.finalized = False
    db.session.commit()

    return jsonify({'message': 'task review submitted'})










# developer ACCEPTS A TASK
@app.route('/tasks/accept', methods=['POST'])
def accept_task():
    data = request.get_json()
    task_id = data.get('task_id')
    developer_address = data.get('address')
    print(data)

    task = Task.query.filter_by(task_id=task_id, developer_address=developer_address, rejected=False, accepted=False).first()

    if not task:
        return jsonify({'error': 'Task not found or already accepted/rejected.'}), 404

    task.accepted = True
    task.ongoing = True
    db.session.commit()

    return jsonify({'message': 'Task accepted successfully.'}), 200

@app.route('/tasks/submit', methods=['POST'])
def submit_task():
    data = request.get_json()
    task_id = data.get('task_id')
    developer_address = data.get('address')
    print(data)

    task = Task.query.filter_by(task_id=task_id, developer_address=developer_address, ongoing=True, rejected=False, accepted=True).first()

    if not task:
        return jsonify({'error': 'Task not found or not accepted.'}), 404

    task.completed = True
    db.session.commit()

    return jsonify({'message': 'Task accepted successfully.'}), 200


# REJECT A TASK
@app.route('/tasks/reject', methods=['POST'])
def reject_task():
    data = request.get_json()
    task_id = data.get('task_id')
    developer_address = data.get('address')

    task = Task.query.filter_by(task_id=task_id, developer_address=developer_address, accepted=False).first()

    if not task:
        return jsonify({'error': 'Task not found or already accepted/rejected.'}), 404

    task.rejected = True
    task.accepted=False
    db.session.commit()

    return jsonify({'message': 'Task rejected successfully.'}), 200



# BUYER CANCELS A TASK
@app.route('/tasks/cancel', methods=['POST'])
def cancel_task():
    data = request.get_json()
    task_id = data.get('task_id')
    buyer_address = data.get('address')

    if not buyer_address:
        return jsonify({'message': 'buyer_address empty'}), 409

    task = Task.query.filter_by(task_id=task_id, buyer_address=buyer_address,cancelled=False, accepted=True, rejected=False, completed=False).first()

    if not task:
        return jsonify({'error': 'Task not found or cannot be cancelled.'}), 404

    task.cancelled = True
    db.session.commit()

    return jsonify({'message': 'Task cancelled successfully.'}), 200

# DEV ABORTS AN ONGOING_TASK
@app.route('/abort', methods=['POST'])
def abort_task():
    data = request.get_json()
    task_id = data.get('task_id')
    buyer_address = data.get('address')
    developer_address = data.get('developer_address')
    if not buyer_address:
        return jsonify({'message': 'buyer_address empty'}), 409
    if not task_id:
        return jsonify({'message': 'task_id empty'}), 409
    if not developer_address:
        return jsonify({'message': 'developer_address empty'}), 409

    task = Task.query.filter_by(task_id=task_id, developer_address=developer_address, buyer_address=buyer_address,canceled=False, accepted=True, rejected=False, completed=False).first()

    if not task:
        return jsonify({'error': 'Task not found or cannot be cancelled.'}), 404

    task.abort = True
    db.session.commit()

    return jsonify({'message': 'Task cancelled successfully.'}), 200


@app.route('/task/pay', methods=['POST'])
def pay():
    data = request.get_json()
    task_id = data.get('task_id')
    address = data.get('agent_address')
    buyer_address = data.get('buyer_address')
    developer_address = data.get('developer_address')
    new_task_id = data.get('new_task_id')
    if not buyer_address:
        return jsonify({'message': 'buyer address empty'}), 401

    if not task_id:
        return jsonify({'message': 'task_id address empty'}), 401

    if not address:
        return jsonify({'message': 'agent_address address empty'}), 401
    check_agent = Agent.query.filter_by(address=address)
    if not check_agent:
        return jsonify({'message': 'address not an agent'}), 401

    if not developer_address:
        return jsonify({'message': 'developer_address address empty'}), 401


    task = Task.query.filter_by(task_id=task_id, buyer_address=buyer_address, abort=False, developer_address=developer_address, accepted=True).first()

    if not task:
        return jsonify({'message': 'task parameters invalid'}), 401

    task.task_id = new_task_id
    task.paid = True
    db.session.commit()
    print(task.paid)

    return jsonify({'message': 'payment successful'})





@app.route('/list_services', methods=['GET'])
def list_services():
    address = request.args.get('address')
    if address:
        user = User.query.filter_by(address=address).first()
        if not user:
            return jsonify({'error': 'User not found'}), 409
        services = Service.query.filter_by(user_address=user.address).all()
    else:
        services = Service.query.all()

    result = []
    for service in services:
        user = User.query.filter_by(address=service.user_address).first()
        result.append({
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'image_file': service.image_file,
            'user': {
                'address': user.address,
                'username': user.username,
                'avatar': user.avatar
            }
        })
    return jsonify(result), 200












# AGENT VIEWS

@app.route('/add_agent', methods=['POST'])
def add_agent():
    username = request.form.get('username')
    agent_address = request.form.get('agent_address')
    avatar = request.files.get('avatar')
    superuser_address = request.form.get('superuser_address')


    superuser = Agent.query.filter_by(address=superuser_address, superAgent=True).first()
    if not superuser:
        return jsonify({'error': "you don't have permission to do this"}), 401

    agent = Agent.query.filter_by(address=agent_address).first()
    if agent:
        return jsonify({'error': 'agent address already exists'}), 409

    existing_user = Agent.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409

    if not avatar:
        return jsonify({'error': 'avatar not present'}), 401

    filename = None
    if avatar:
        filename = secure_filename(avatar.filename)
        avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        avatar.save(avatar_path)
        avatar_url = f'/uploads/{filename}'

    new_agent = Agent(address=agent_address, avatar=avatar_url, username=username)
    db.session.add(new_agent)
    db.session.commit()

    return jsonify({'success': 'agent added successfully', 'avatar': avatar_url})


@app.route('/agent_tasks/<address>', methods=['GET'])
def agent_tasks(address):
    tasks = Task.query.filter_by(agent_address=address).all()
    result = []
    for task in tasks:
        user = User.query.filter_by(address=task.buyer_address).first()
        developer = User.query.filter_by(address=task.developer_address).first()
        result.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'price': str(task.price),
            'finalized': task.finalized,
            'accepted': task.accepted,
            'completed': task.completed,
            'rejected': task.rejected,
            'paid': task.paid,
            'abort': task.abort,
            'canceled': task.canceled,
            'ongoing': task.ongoing,
            'deadline': str(task.deadline),
            'buyer': {
                'address': user.address,
                'username': user.username,
                'avatar': user.avatar
            },
            'developer': {
                'address': developer.address,
                'username': developer.username,
                'avatar': developer.avatar
            }
        })
    return jsonify(result), 200


@app.route('/agent/dashboard/<address>', methods=['GET'])
def agent_dashboard(address):
    if not address:
        return jsonify({'message': 'agent address empty'}), 401
    agent = Agent.query.filter_by(address=address)

    if not agent:
        return jsonify({'message': 'not an agent'})

    tasks = Task.query.all()

    result = []
    for task in tasks:
        user = User.query.filter_by(address=task.buyer_address).first()
        developer = User.query.filter_by(address=task.developer_address).first()
        result.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'price': str(task.price),
            'finalized': task.finalized,
            'accepted': task.accepted,
            'completed': task.completed,
            'rejected': task.rejected,
            'paid': task.paid,
            'abort': task.abort,
            'canceled': task.canceled,
            'ongoing': task.ongoing,
            'deadline': str(task.deadline),
            'buyer': {
                'address': user.address,
                'username': user.username,
                'avatar': user.avatar
            },
            'developer': {
                'address': developer.address,
                'username': developer.username,
                'avatar': developer.avatar
            }
        })

    return jsonify(result)










if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the table
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.run(host='0.0.0.0', port=8000, debug=True)