from flask import request, send_file
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models.cloud import *
from config import KEY
from werkzeug.utils import secure_filename


class Upload(Resource):
    @jwt_required()
    def post(self, key, choice):
        if key == KEY:
            if 'file' in request.files or secure_filename(file.filename) != '':
                file = request.files['file']
                return upload(choice, file)
            return {'message': 'no file selected for uploading'}, 400
        return {'message': 'unauthorized access'}, 401


class Files(Resource):
    def get(self, key, choice, id):
        if key == KEY:
            return download(choice, id)
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def put(self, key, choice, id):
        if key == KEY:
            if 'file' in request.files or secure_filename(file.filename) != '':
                file = request.files['file']
                return edit(choice, id, file)
            return {'message': 'no file selected for uploading'}, 400
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def delete(self, key, choice, id):
        if key == KEY:
            return remove(choice, id)
        return {'message': 'unauthorized access'}, 401
