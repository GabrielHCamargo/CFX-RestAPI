import os
from flask import request, send_from_directory
from config import id_generator
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['pdf', 'png', 'webp', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'])
PATH = os.path.join(os.getcwd(), 'cloud')

def upload(choice, file):
    if file and allowed_file(secure_filename(file.filename)):
        try:
            filename = rename(secure_filename(file.filename))
            file.save(os.path.join(PATH, choice, secure_filename(filename)))
            return {'message': secure_filename(filename)}, 201    
        except BaseException as error:
            return {'message': f"unexpected {error}, {type(error)}"}, 502        
    else:
        return {'message': 'allowed file types are pdf, png, jpg, jpeg, gif'}


def download(choice, id):
    if send_from_directory(os.path.join(PATH, choice), secure_filename(id), as_attachment=False):
        try:
            return send_from_directory(os.path.join(PATH, choice), secure_filename(id), as_attachment=False)
        except BaseException as error:
            return {'message': f"unexpected {error}, {type(error)}"}, 502
    else:
        return {'message': "file not found"}, 404


def edit(choice, id, file):
    if send_from_directory(os.path.join(PATH, choice), secure_filename(id), as_attachment=False) and file:
        try:
            file.save(os.path.join(PATH, choice, secure_filename(id)))
            return {'message': 'file updated'}, 200
        except BaseException as error:
            return {'message': f"unexpected {error}, {type(error)}"}, 502
    return {'message': 'no file part in the request'}, 404


def remove(choice, id):
    if send_from_directory(os.path.join(PATH, choice), secure_filename(id), as_attachment=False):
        try:
            os.remove(os.path.join(PATH, choice, secure_filename(id)))
            return {'message': 'file deleted'}, 200
        except BaseException as error:
            return {'message': f"unexpected {error}, {type(error)}"}, 502
    return {'message': 'file not found'}, 401



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def rename(file):
    name, extension = os.path.splitext(file)
    new_filename = id_generator(None)   
    return str(new_filename) + extension