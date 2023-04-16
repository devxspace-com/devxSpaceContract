import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.utils import secure_filename
from sqlalchemy import Interval
from datetime import timedelta

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Iamsuperman:devxspace@Iamsuperman.mysql.pythonanywhere-services.com/Iamsuperman$devxspace'

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.secret_key = os.urandom(24)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# def get_account():
#     with app.app_context():
#         web3 = Web3()
#         if web3.is_connected():
#             accounts = web3.eth.accounts
#             if len(accounts) > 0:
#                 account = accounts[0]
#                 return account
#             else:
#                 return 'No Ethereum accounts found'
#         else:
#             return 'Could not connect to Ethereum network'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(42), nullable=False, unique=True)
    avatar = db.Column(db.String(20), nullable=True)
    username = db.Column(db.String(20), nullable=True, unique=True)
    about = db.Column(db.String(255), nullable=True)
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

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Integer)
    accepted = db.Column(db.Boolean, default=False)
    completed = db.Column(db.Boolean, default=False)
    rejected = db.Column(db.Boolean, default=False)
    ongoing = db.Column(db.Boolean, default=False)
    deadline = db.Column(Interval)
    developer_address = db.Column(db.String(42), nullable=False)
    buyer_address = db.Column(db.String(42), db.ForeignKey('user.address'), nullable=False)

    def __repr__(self):
        return f"Task {self.id}, Title: {self.title}, Status: {self.status}"


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"Task {self.id}, Title: {self.name}, user_id: {self.user_id}"


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

    if not developer_address:
        return jsonify({'message': 'gettat abeg'}), 401


    task = Task(title=title, description=description, price=price, deadline=time_frame, buyer_address=buyer_address, developer_address=developer_address)
    db.session.add(task)
    db.session.commit()

    return jsonify({'message': 'Task created successfully.'}), 200


# LIST OF TASKS AVAILABLE TO A USER
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
            'id': task.id,
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


@app.route('/ongoing_tasks/<address>', methods=['GET'])
def get_ongoing_tasks(address):
    # Check if user exists
    user = User.query.filter_by(address=address).first()
    if not user:
        return jsonify({'message': 'user not found'}), 401

    # Get available tasks for developer
    ongoing_tasks = Task.query.filter_by(developer_address=address, accepted=True, rejected=False, completed=False, ongoing=True).all()

    tasks = []
    for task in ongoing_tasks:
        # Query User table to get username of buyer_address
        buyer = User.query.filter_by(address=task.buyer_address).first()
        tasks.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'price': task.price,
            'completed': task.completed,
            'ongoing': task.ongoing,
            'rejected': task.rejected,
            'deadline': task.deadline.total_seconds(),
            'buyer_address': task.buyer_address,
            'buyer_username': buyer.username
        })

    return jsonify({'tasks': tasks}), 200









# ACCEPT A TASK
@app.route('/tasks/accept', methods=['POST'])
def accept_task():
    data = request.get_json()
    task_id = data.get('task_id')
    developer_address = data.get('address')
    print(data)

    task = Task.query.filter_by(id=task_id, developer_address=developer_address, rejected=False, accepted=False).first()

    if not task:
        return jsonify({'error': 'Task not found or already accepted/rejected.'}), 404

    task.accepted = True
    task.ongoing = True
    db.session.commit()

    return jsonify({'message': 'Task accepted successfully.'}), 200

@app.route('/tasks/submit', methods=['POST'])
def accept_task():
    data = request.get_json()
    task_id = data.get('task_id')
    developer_address = data.get('address')
    print(data)

    task = Task.query.filter_by(id=task_id, developer_address=developer_address, ongoing=True, rejected=False, accepted=True).first()

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

    task = Task.query.filter_by(id=task_id, developer_address=developer_address, accepted=False).first()

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
    user_address = data.get('address')

    task = Task.query.filter_by(id=task_id, owner_address=user_address, accepted=False, rejected=False, completed=False).first()

    if not task:
        return jsonify({'error': 'Task not found or cannot be cancelled.'}), 404

    task.cancelled = True
    db.session.commit()

    return jsonify({'message': 'Task cancelled successfully.'}), 200



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




if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the table
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.run(host='0.0.0.0', port=8000, debug=True)