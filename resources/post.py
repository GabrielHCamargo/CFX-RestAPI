from flask_restful import Resource, reqparse
from models.post import PostModel
from config import id_generator, KEY
from flask_jwt_extended import jwt_required
from datetime import datetime


argument = reqparse.RequestParser()
argument.add_argument('profile', type=str)
argument.add_argument('name', type=str)
argument.add_argument('media', type=str, required=True)
argument.add_argument('text', type=str, required=True)


# /API_KEY/post/ID
class Post(Resource):
    @jwt_required()
    def post(self, key, id):
        if key == KEY:
            if id == 'create':
                data = argument.parse_args()
                id = id_generator(data['text'])
                date = datetime.today().strftime('%d-%m-%Y %H:%M')
                if PostModel.search(str(id)) is None:
                    post = {
                        'id': str(id),
                        'profile': data['profile'],
                        'name': data['name'],
                        'media': data['media'],
                        'text': data['text'],
                        'datetime': date,
                        'status': 'activated',
                    }
                    try:
                        post = PostModel(**post)
                        post.save()
                        return {'message': 'post created'}, 201
                    except BaseException as error:
                        return {'message': f"Unexpected {error}, {type(error)}"}, 502
                return {'message': 'post already exist'}, 400
            return {'message': 'check your request'}, 409
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def get(self, key, id):
        if key == KEY:
            post = PostModel.search(id)
            if post and post.status != 'disabled':
                return {'message': post.json()}, 200
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def put(self, key, id):
        if key == KEY:
            data = argument.parse_args()
            data = {
                'media': data['media'],
                'text': data['text'],
                'status': 'activated',
            }
            post = PostModel.search(id)
            if post and post.status != 'disabled':
                try:
                    post.update(**data)
                    post.save()
                    return {'message': 'updated post'}, 200
                except BaseException as error:
                    return {'message': f"Unexpected {error}, {type(error)}"}, 502
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def delete(self, key, id):
        if key == KEY:
            post = PostModel.search(id)
            if post and post.status != 'disabled':
                try:
                    data = {
                        'media': post.media,
                        'text': post.text,
                        'status': 'disabled',
                    }
                    post.update(**data)
                    post.save()
                    return {'message': 'post disabled'}, 200
                except BaseException as error:
                    return {'message': f"Unexpected {error}, {type(error)}"}, 502
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401


# /API_KEY/posts
class Posts(Resource):
    @jwt_required()
    def get(self, key):
        if key == KEY:
            posts = [post.json() for post in PostModel.query.all()
                     if post.status != 'disabled']
            return {'message': posts}, 200
        return {'message': 'unauthorized access'}, 401
