from flask_restful import Resource, reqparse
from models.message import MessageModel
from config import id_generator, KEY
from flask_jwt_extended import jwt_required
from datetime import datetime


argument = reqparse.RequestParser()
argument.add_argument('id_user', type=str, required=True)
argument.add_argument('id_chat', type=str, required=True)
argument.add_argument('text', type=str, required=True)


# /API_KEY/message/ID
class Message(Resource):
    @jwt_required()
    def post(self, key, id):
        if key == KEY:
            if id == 'create':
                data = argument.parse_args()
                date = datetime.today().strftime('%d-%m-%Y %H:%M')
                id = id_generator(data['text'] + data['id_user'] + date)
                if MessageModel.search(str(id)) is None:
                    message = {
                        'id': str(id),
                        'id_user': data['id_user'],
                        'id_chat': data['id_chat'],
                        'text': data['text'],
                        'datetime': date,
                        'status': 'activated',
                    }
                    try:
                        message = MessageModel(**message)
                        message.save()
                        return {'message': message.json()}, 201
                    except BaseException as error:
                        return {'message': f"Unexpected {error}, {type(error)}"}, 502
                return {'message': 'message already exist'}, 400
            return {'message': 'check your request'}, 409
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def get(self, key, id):
        if key == KEY:
            message = MessageModel.search(id)
            if message and message.status != 'disabled':
                return {'message': message.json()}, 200

            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def delete(self, key, id):
        if key == KEY:
            message = MessageModel.search(id)
            if message and message.status != 'disabled':
                try:
                    message.update('disabled')
                    message.save()
                    return {'message': 'message disabled'}, 200
                except BaseException as error:
                    return {'message': f"Unexpected {error}, {type(error)}"}, 502

            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401


# /API_KEY/message
class Messages(Resource):
    @jwt_required()
    def get(self, key):
        if key == KEY:
            messages = [message.json() for message in MessageModel.query.all(
            ) if message.status != 'disabled']
            return {'message': messages}, 200
        return {'message': 'unauthorized access'}, 401
