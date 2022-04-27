from flask_restful import Resource, reqparse
from models.chat import ChatModel
from flask_jwt_extended import jwt_required
from config import id_generator, convert_string, convert_list, KEY


argument = reqparse.RequestParser()
argument.add_argument('title', type=str)
argument.add_argument('cover', type=str)
argument.add_argument('users', action='append')
argument.add_argument('status', type=str)


# /API_KEY/chat/ID
class Chat(Resource):
    @jwt_required()
    def post(self, key, id):
        if key == KEY:
            if id == 'create':
                data = argument.parse_args()

                # PROCESSO PARA ARMAZENAR NO SQLITE
                data['users'] = convert_string(data['users'])

                id = id_generator(data['title'])
                if ChatModel.search(str(id)) is None:
                    try:
                        chat = ChatModel(str(id), **data)
                        chat.save()
                        return {'message': 'chat created'}, 201
                    except BaseException as error:
                        return {'message': f"Unexpected {error}, {type(error)}"}, 502
                return {'message': 'chat already exist'}, 400
            return {'message': 'check your request'}, 409
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def get(self, key, id):
        if key == KEY:
            chat = ChatModel.search(id)
            if chat and chat.status != 'disabled':
                chat = chat.json()

                # PROCESSO PARA RETORNAR DO SQLITE
                chat['users'] = convert_list(chat['users'])

                return {'message': chat}, 200
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def put(self, key, id):
        if key == KEY:
            data = argument.parse_args()

            # PROCESSO PARA ARMAZENAR NO SQLITE
            data['users'] = convert_string(data['users'])

            chat = ChatModel.search(id)
            if chat and chat.status != 'disabled':
                try:
                    chat.update(**data)
                    chat.save()
                    return {'message': 'updated chat'}, 200
                except BaseException as error:
                    return {'message': f"Unexpected {error}, {type(error)}"}, 502
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def delete(self, key, id):
        if key == KEY:
            chat = ChatModel.search(id)
            if chat and chat.status != 'disabled':
                data = {
                    "title": chat.title,
                    "cover": chat.cover,
                    "users": chat.users,
                    "status": "disabled"
                }
                try:
                    chat.update(**data)
                    chat.save()
                    return {'message': 'chat disabled'}, 200
                except BaseException as error:
                    return {'message': f"Unexpected {error}, {type(error)}"}, 502
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401


# /API_KEY/chats
class Chats(Resource):
    @jwt_required()
    def get(self, key):
        if key == KEY:
            chats = [chat.json() for chat in ChatModel.query.all()
                     if chat.status != 'disabled']

            # PROCESSO PARA RETORNAR DO SQLITE
            for chat in chats:
                chat['users'] = convert_list(chat['users'])

            return {'message': chats}, 200
        return {'message': 'unauthorized access'}, 401
