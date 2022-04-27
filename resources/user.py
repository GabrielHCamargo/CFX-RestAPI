from datetime import datetime
from flask_restful import Resource, reqparse
from models.user import UserModel
from models.client import ClientModel
from models.payment import PaymentModel, payment, contract
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt
from werkzeug.security import safe_str_cmp
from config import BLOCKLIST, id_generator, KEY


argument = reqparse.RequestParser()
argument.add_argument('id_client', type=str)
argument.add_argument('name', type=str)
argument.add_argument('doc', type=str)
argument.add_argument('email', type=str, required=True)
argument.add_argument('password', type=str)
argument.add_argument('status', type=str)


# /API_KEY/user/ID
class User(Resource):
    @jwt_required()
    def get(self, key, id):
        if key == KEY:
            user = UserModel.search(id)
            if user and user.status != 'disabled':
                return {'message': user.json()}, 200
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def put(self, key, id):
        if key == KEY:
            data = argument.parse_args()
            user = UserModel.search(id)
            if user and user.status != 'disabled':
                try:
                    user.update(**data)
                    user.save()
                    return {'message': 'user updated'}, 200
                except BaseException as error:
                    return {'message': f"Unexpected {error}, {type(error)}"}, 502
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def delete(self, key, id):
        if key == KEY:
            user = UserModel.search(id)
            if user and user.status != 'disabled':
                data = {
                    'id_client': None,
                    'name': user.name,
                    'doc': '',
                    'email': user.email,
                    'password': '',
                    'status': 'disabled',
                }
                try:
                    user.update(**data)
                    user.save()
                    return {'message': 'user disabled'}, 200
                except BaseException as error:
                    return {'message': f"Unexpected {error}, {type(error)}"}, 502
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401


# /API_KEY/user/register
class UserRegister(Resource):
    def post(self, key):
        if key == KEY:
            data = argument.parse_args()
            id = id_generator(data['email'])
            id_client = ClientModel.client(data['doc'])
            if UserModel.search(str(id)) is None:
                if id_client:
                    user = {
                        'id': str(id),
                        'id_client': id_client,
                        'name': data['name'],
                        'doc': data['doc'],
                        'email': data['email'],
                        'password': data['password'],
                        'status': 'activated',
                    }
                    try:
                        user = UserModel(**user)
                        user.save()
                        return {'message': 'user created'}, 201
                    except BaseException as error:
                        user.delete()
                        return {'message': f"Unexpected {error}, {type(error)}"}, 502

                # VALIDAR SE FOI PAGO
                pay_contract = contract(data['doc'])
                if pay_contract and pay_contract['status'] == 'Em dia':
                    id_client = id_generator(data['doc'])
                    user = {
                        'id': str(id),
                        'id_client': str(id_client),
                        'name': data['name'],
                        'doc': data['doc'],
                        'email': data['email'],
                        'password': data['password'],
                        'status': 'activated',
                    }
                    if len(data['doc']) == 14:
                        person = 'PJ'
                    else:
                        person = 'PF'
                    client = {
                        'id': str(id_client),
                        'name': data['name'],
                        'type': person,
                        'doc': data['doc'],
                        'email': data['email'],
                        'phone': pay_contract['phone'],
                        'groups': "",
                        'api_key': "",
                        'api_secret': "",
                        'status': "activated"
                    }
                    try:
                        user = UserModel(**user)
                        client = ClientModel(**client)
                        user.save()
                        client.save()
                        return {'message': 'user and client created'}, 201
                    except BaseException as error:
                        user.delete()
                        client.delete()
                        return {'message': f"Unexpected {error}, {type(error)}"}, 502
                user = {
                    'id': str(id),
                    'id_client': None,
                    'name': data['name'],
                    'doc': data['doc'],
                    'email': data['email'],
                    'password': data['password'],
                    'status': 'free',
                }
                try:
                    user = UserModel(**user)
                    user.save()
                    return {'message': 'user created'}, 201
                except BaseException as error:
                    user.delete()
                    return {'message': f"Unexpected {error}, {type(error)}"}, 502
            return {'message': 'user already exists'}, 400
        return {'message': 'unauthorized access'}, 401


# /API_KEY/user/login
class UserLogin(Resource):
    @classmethod
    def post(cls, key):
        if key == KEY:
            data = argument.parse_args()
            id = id_generator(data['email'])
            user = UserModel.search(str(id))
            if user and user.status != 'disabled' and safe_str_cmp(user.password, data['password']):
                access_token = create_access_token(identity=user.id)
                refresh_token = create_refresh_token(identity=user.id)
                return {
                    'message': {
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'id': user.id,
                    },
                }, 200
            return {'message': 'the email or password incorrect'}, 401
        return {'message': 'unauthorized access'}, 401


# /API_KEY/user/logout
class UserLogout(Resource):
    @jwt_required()
    def post(self, key):
        if key == KEY:
            jwt_id = get_jwt()['jti']
            BLOCKLIST.add(jwt_id)
            return {'message': 'logged out ok'}, 200
        return {'message': 'unauthorized access'}, 401
