import os
from datetime import timedelta
from config import search, database, BLOCKLIST, JWT_SECRET_KEY, USER, PASSWORD, HOST, PORT, DATABASE
from flask import Flask, jsonify, render_template
from flask_restful import Api
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from resources.admin import Admin, AdminRegister, AdminLogin, AdminLogout
from resources.client import Client, ClientRegister, ClientKeys, ClientDocument, Clients
from resources.group import Group, GroupRegister, Groups
from resources.user import User, UserRegister, UserLogin, UserLogout
from resources.post import Post, Posts
from resources.chat import Chat, Chats
from resources.cloud import Upload, Files
from resources.message import Message, Messages
from resources.payment import Payment


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_BLOCKLIST_ENABLED'] = True
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 35,
    'pool_timeout': 7,
    'pool_pre_ping': True
}
database.init_app(app)
api = Api(app)
jwt = JWTManager(app)


@app.before_first_request
def create_database():
    database.create_all()


@jwt.token_in_blocklist_loader
def check_blocklist(self, token):
    return token['jti'] in BLOCKLIST


@jwt.revoked_token_loader
def invalid_access_token(jwt_header, jwt_payload):
    return jsonify({'message': 'You have been logged out.'}), 401


@app.route('/<string:key>/auth/<string:id>', methods=["POST"])
@jwt_required(refresh=True)
def auth(key, id):
    if search(id):
        access_token = create_access_token(identity=id)
        return {'message': {'access_token': access_token}}, 200
    return {'message': 'id not found'}, 404


@app.route('/', methods=['GET'])
@app.route('/<string:id>', methods=['GET'])
def index(id=None):
    if id == 'cryptocurrency_market':
        return render_template('cryptocurrency_market.html'), 200
    if id == 'graphic_analysis':
        return render_template('graphic_analysis.html'), 200
    if id == 'screener':
        return render_template('screener.html'), 200
    return '<h1>HTTP/1.0 403 Forbidden</h1>', 403


api.add_resource(Admin, '/<string:key>/admin/<string:id>')
api.add_resource(AdminRegister, '/<string:key>/admin/register')
api.add_resource(AdminLogin, '/<string:key>/admin/login')
api.add_resource(AdminLogout, '/<string:key>/admin/logout')
api.add_resource(Client, '/<string:key>/client/<string:id>')
api.add_resource(ClientRegister, '/<string:key>/client/register')
api.add_resource(ClientKeys, '/<string:key>/client/keys/<string:id>')
api.add_resource(ClientDocument, '/<string:key>/client/document')
api.add_resource(Clients, '/<string:key>/clients')
api.add_resource(Group, '/<string:key>/group/<string:id>')
api.add_resource(GroupRegister, '/<string:key>/group/create')
api.add_resource(Groups, '/<string:key>/groups')
api.add_resource(User, '/<string:key>/user/<string:id>')
api.add_resource(UserRegister, '/<string:key>/user/register')
api.add_resource(UserLogin, '/<string:key>/user/login')
api.add_resource(UserLogout, '/<string:key>/user/logout')
api.add_resource(Post, '/<string:key>/post/<string:id>')
api.add_resource(Posts, '/<string:key>/posts')
api.add_resource(Chat, '/<string:key>/chat/<string:id>')
api.add_resource(Chats, '/<string:key>/chats')
api.add_resource(Message, '/<string:key>/message/<string:id>')
api.add_resource(Messages, '/<string:key>/messages')
api.add_resource(Upload, '/<string:key>/file-upload/<string:choice>')
api.add_resource(Files, '/<string:key>/files/<string:choice>/<string:id>')
api.add_resource(Payment, '/<string:key>/payment/<string:id>')


if __name__ == '__main__':
    PORT = int(os.getenv('PORT'), '5000')
    app.run(host='0.0.0.0', port=PORT)
