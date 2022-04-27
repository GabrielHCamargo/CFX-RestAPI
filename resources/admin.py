from flask_restful import Resource, reqparse
from models.admin import AdminModel
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt
from flask_jwt_extended import jwt_required
from werkzeug.security import safe_str_cmp
from config import BLOCKLIST, id_generator, KEY


argument = reqparse.RequestParser()
argument.add_argument('name', type=str)
argument.add_argument('login', type=str, required=True)
argument.add_argument('email', type=str)
argument.add_argument('password', type=str, required=True)
argument.add_argument('profile', type=str)

# /API_KEY/admin/register
class AdminRegister(Resource):
    @jwt_required()
    def post(self, key):
        if key == KEY:
            data = argument.parse_args()
            id = id_generator(data['login'])
            if AdminModel.search(str(id)) is None:
                data = {
                    'id': str(id),
                    'name': data['name'],
                    'login': data['login'],
                    'email': data['email'],
                    'password': data['password'],
                    'profile': data['profile'],
                    'status': 'activated',
                }
                admin = AdminModel(**data)
                try:
                    admin.save()
                    return {'message': 'admin created'}, 201
                except BaseException as error:
                    return {'message': f"Unexpected {error}, {type(error)}"}, 502
            return {'message': 'admin already exist'}, 400
        return {'message': 'unauthorized access'}, 401


# /API_KEY/admin/login
class AdminLogin(Resource):
    @classmethod
    def post(cls, key):
        if key == KEY:
            data = argument.parse_args()
            id = id_generator(data['login'])
            admin = AdminModel.search(str(id))
            if admin and admin.status != 'disabled' and safe_str_cmp(admin.password, data['password']):
                access_token = create_access_token(identity=admin.id)
                refresh_token = create_refresh_token(identity=admin.id)
                return {
                    'message': {
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'id': admin.id,
                    },
                }, 200
            return {'message': 'The login e/or password incorrect'}, 404
        return {'message': 'unauthorized access'}, 401


# /API_KEY/admin/ID
class Admin(Resource):
    @jwt_required()
    def get(self, key, id):
        if key == KEY:
            admin = AdminModel.search(id)
            if admin and admin.status != 'disabled':
                return {'message': admin.json()}, 200
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def delete(self, key, id):
        if key == KEY:
            admin = AdminModel.search(id)
            if admin and admin.status != 'disabled':
                try:
                    edit = {
                        'profile': admin.profile,
                        'status': 'disabled',
                    }
                    admin.update(edit)
                    admin.save()
                    return {'message': 'admin disabled'}, 200
                except BaseException as error:
                    return {'message': f"Unexpected {error}, {type(error)}"}, 502
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401


# /API_KEY/admin/logout
class AdminLogout(Resource):
    @jwt_required()
    def post(self, key):
        if key == KEY:
            jwt_id = get_jwt()['jti']
            BLOCKLIST.add(jwt_id)
            return {'message': 'logged out ok'}, 200
        return {'message': 'unauthorized access'}, 401
