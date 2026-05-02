from flask import Blueprint, request, jsonify
from .models import Admin, Opportunity
from .extensions import db, bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask import Blueprint, request, jsonify
from flask import render_template

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    return "Server Running"

@routes.route('/signup', methods=['POST'])
def signup():
    data = request.json

    if not data.get('full_name') or not data.get('email') or not data.get('password') or not data.get('confirm_password'):
        return jsonify({'error': 'All fields required'}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        return jsonify({'error': 'Invalid email'}), 400

    if len(data['password']) < 8 or data['password'] != data['confirm_password']:
        return jsonify({'error': 'Password invalid'}), 400

    if Admin.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Account exists'}), 400

    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    admin = Admin(full_name=data['full_name'], email=data['email'], password=hashed)

    db.session.add(admin)
    db.session.commit()

    return jsonify({'message': 'Signup success'})

@routes.route('/login', methods=['POST'])
def login():
    data = request.json
    admin = Admin.query.filter_by(email=data.get('email')).first()

    if not admin or not bcrypt.check_password_hash(admin.password, data.get('password')):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = create_access_token(identity=str(admin.id))
    return jsonify({'token': token})

@routes.route('/opportunities', methods=['POST'])
@jwt_required()
def create_opportunity():
    admin_id = int(get_jwt_identity())
    data = request.json

    required = ['name','duration','start_date','description','skills','category','future_opportunities']
    for r in required:
        if not data.get(r):
            return jsonify({'error': 'Missing fields'}), 400

    opp = Opportunity(
        name=data['name'],
        duration=data['duration'],
        start_date=data['start_date'],
        description=data['description'],
        skills=data['skills'],
        category=data['category'],
        future_opportunities=data['future_opportunities'],
        max_applicants=data.get('max_applicants'),
        admin_id=admin_id
    )

    db.session.add(opp)
    db.session.commit()

    return jsonify({'message': 'Created'})

@routes.route('/opportunities', methods=['GET'])
@jwt_required()
def get_all():
    admin_id = get_jwt_identity()
    data = Opportunity.query.filter_by(admin_id=admin_id).all()

    result = []
    for o in data:
        result.append({
            'id': o.id,
            'name': o.name,
            'duration': o.duration,
            'start_date': o.start_date,
            'description': o.description,
            'skills': o.skills,
            'category': o.category,
            'future_opportunities': o.future_opportunities,
            'max_applicants': o.max_applicants
        })

    return jsonify(result)
@routes.route('/opportunities/<int:id>', methods=['PUT'])
@jwt_required()
def update(id):
    admin_id = int(get_jwt_identity())
    o = Opportunity.query.filter_by(id=id, admin_id=admin_id).first()

    if not o:
        return jsonify({'error': 'Not found'}), 404

    data = request.json

    o.name = data.get('name', o.name)
    o.duration = data.get('duration', o.duration)
    o.start_date = data.get('start_date', o.start_date)
    o.description = data.get('description', o.description)
    o.skills = data.get('skills', o.skills)
    o.category = data.get('category', o.category)
    o.future_opportunities = data.get('future_opportunities', o.future_opportunities)
    o.max_applicants = data.get('max_applicants', o.max_applicants)

    db.session.commit()

    return jsonify({'message': 'Updated'})
@routes.route('/opportunities/<int:id>', methods=['DELETE'])
@jwt_required()
def delete(id):
    admin_id = int(get_jwt_identity())
    o = Opportunity.query.filter_by(id=id, admin_id=admin_id).first()

    if not o:
        return jsonify({'error': 'Not found'}), 404

    db.session.delete(o)
    db.session.commit()

    return jsonify({'message': 'Deleted'})
@routes.route('/opportunities/<int:id>', methods=['GET'])
@jwt_required()
def get_one(id):
    admin_id = int(get_jwt_identity())
    o = Opportunity.query.filter_by(id=id, admin_id=admin_id).first()

    if not o:
        return jsonify({'error': 'Not found'}), 404

    return jsonify({
        'id': o.id,
        'name': o.name,
        'duration': o.duration,
        'start_date': o.start_date,
        'description': o.description,
        'skills': o.skills,
        'category': o.category,
        'future_opportunities': o.future_opportunities,
        'max_applicants': o.max_applicants
    })
main = Blueprint('main', __name__)

@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    # temporary check
    if email == "admin@gmail.com" and password == "1234":
        return jsonify({"message": "Login success"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@main.route('/')
def home():
    return render_template('admin.html')