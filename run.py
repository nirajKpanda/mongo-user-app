import json
from flask_mongoengine import MongoEngine
from mongoengine.queryset.visitor import Q
from flask_user import login_required, UserManager, UserMixin
from flask import Flask, render_template_string, jsonify, request


# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'XXXXXXXXX'

    # Flask-MongoEngine settings
    MONGODB_SETTINGS = {
        'db': 'MyDb',
        'host': 'mongodb://localhost:27017/MyDb'
    }

    # Flask-User settings
    USER_APP_NAME = "User Management System"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False      # Disable email authentication
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form


def create_app():
    """ Flask application factory """
    
    # Setup Flask and load app.config
    app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')

    # Setup Flask-MongoEngine
    db = MongoEngine(app)

    # Define the User document.
    # NB: Make sure to add flask_user UserMixin !!!
    class User(db.Document, UserMixin):
        active = db.BooleanField(default=True)

        # User authentication information
        username = db.StringField(default='')
        password = db.StringField()

        # User information
        first_name = db.StringField(default='')
        last_name = db.StringField(default='')

        # Relationships
        roles = db.ListField(db.StringField(), default=[])

        # other details
        email = db.EmailField(default='admin@user-app.com')
        phone = db.IntField(default=1234567890)
        eid = db.IntField(default=12345)
        address = db.StringField(default='520-Bakers Square:London')
        zipcode = db.IntField(default=12345)

    # Setup Flask-User and specify the User data-model
    user_manager = UserManager(app, db, User)

    # The Home page is accessible to anyone
    @app.route('/')
    def home_page():
        # String-based templates
        return render_template_string("""
            {% extends "flask_user_layout.html" %}
            {% block content %}
                <h2>Home page</h2>
                <p><a href={{ url_for('user.register') }}>Register</a></p>
                <p><a href={{ url_for('user.login') }}>Sign in</a></p>
                <p><a href={{ url_for('home_page') }}>Home page</a> (accessible to anyone)</p>
                <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
            {% endblock %}
            """)

    # user managements endpoints
    @app.route('/retrive-user-details', methods=['GET'])
    #@login_required    # User must be authenticated
    def retrive_user():
        if request.args['type'] == 'all_users':
            print('fetching all users')
            users = User.objects()
            users = list(set([rec['username'] for rec in users]))
            return jsonify(data=users)
        elif request.args['type'] == 'with_user_details':
            print('fetching user details.....')
            attrib = request.args['attrib']
            value = request.args['value']
            query = {attrib:value}
            users = User.objects(Q(**query))
            #users = User.objects(username='niraj')
            users = list(set([rec['username'] for rec in users]))
            return jsonify(data=users)

    @app.route('/user-management', methods=['POST','PUT', 'DELETE'])
    #@login_required    # User must be authenticated
    def manage_user():
        if request.method == 'POST':
            data = request.data
            data = json.loads(data)
            try:
                User(username=data['uname'],
                    password=data['pass'],
                    first_name=data['fname'],
                    last_name=data['lname'],
                    roles=data['roles'],
                    email=data['email'],
                    phone=data['phone'],
                    eid=data['eid'],
                    address=data['address'],
                    zipcode=data['zipcode']
                ).save()
                status = 'Record/s saved!!'
            except Exception as e:
                print('Experienced : {}'.format(e))
                status = str(e)
            else:
                pass
            finally:
                return jsonify([{'status':status}])
        elif request.method == 'PUT':
            try:
                attrib = request.args['attrib']
                value = request.args['value']
                _filter = {attrib:value}
                col = request.args['col']
                col_val = request.args['col_val']
                _set = {col:col_val}
                result = User.objects(Q(**_filter)).update(Q(**_set))
                status = 'Success'
            except Exception as e:
                status = str(e)
            else:
                pass
            finally:
                return jsonify([{'status':status}])
        elif request.method == 'DELETE':
            user = request.args['username']
            User.objects(username=user).delete()
            return jsonify([{'status':'Records removed!!!'}])
        else:
            return jsonify([{'error':'Found unsupported HTTP method!!!'}])

    return app


# Start development web server
if __name__=='__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
