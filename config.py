import os
import json
import uuid
from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

BLOCKLIST = set()


with open(os.path.join(os.getcwd(), 'config.json')) as file:
    config = json.load(file)


PATH = os.path.join(os.getcwd(), 'cloud')
USER = config.get('USER')
PASSWORD = config.get('PASSWORD')
DATABASE = config.get('DATABASE')
HOST = config.get('HOST')
PORT = config.get('PORT')
JWT_SECRET_KEY = config.get('JWT_SECRET_KEY')
KEY = config.get('KEY')
PUBLIC_KEY_EDUZZ = config.get('PUBLIC_KEY_EDUZZ')
API_KEY_EDUZZ = config.get('API_KEY_EDUZZ')
EMAIL = config.get('EMAIL')


def id_generator(data):
    if data is not None:
        return uuid.uuid5(uuid.NAMESPACE_DNS, data)
    return uuid.uuid4()


def convert_string(data):
    return ', '.join(data).replace(',','')
    

def convert_list(data):
    return data.split()



def search(id):
    from models.admin import AdminModel
    from models.user import UserModel
    
    admin = AdminModel.search(id)
    user = UserModel.search(id)
    if admin and admin.status != 'disabled':
        return True
    elif user and user.status != 'disabled':
        return True
    else:
        return False