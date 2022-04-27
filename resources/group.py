from flask_restful import Resource, reqparse
from models.group import GroupModel
from models.client import ClientModel
from flask_jwt_extended import jwt_required
from config import id_generator, convert_string, convert_list, KEY


argument = reqparse.RequestParser()
argument.add_argument('title', type=str)
argument.add_argument('description', type=str)
argument.add_argument('clients', action='append')
argument.add_argument('status', type=str)


# /API_KEY/group/register
class GroupRegister(Resource):
    @jwt_required()
    def post(self, key):
        if key == KEY:
            data = argument.parse_args()
            id = id_generator(data['title'])
            response = register_group_clients(data['clients'], id)
            if response == True:

                # PROCESSO PARA ARMAZENAR NO SQLITE
                data['clients'] = convert_string(data['clients'])

                if GroupModel.search(str(id)) is None:
                    group = GroupModel(str(id), **data)
                    try:
                        group.save()
                        return {'message': 'group created'}, 201
                    except BaseException as error:
                        return {'message': f"Unexpected {error}, {type(error)}"}, 502
                return {'message': 'group already exist'}, 400
            return response
        return {'message': 'unauthorized access'}, 401


# /API_KEY/group/ID
class Group(Resource):
    @jwt_required()
    def get(self, key, id):
        if key == KEY:
            group = GroupModel.search(id)
            if group and group.status != 'disabled':
                group = group.json()

                # PROCESSO PARA RETORNAR DO SQLITE
                group['clients'] = convert_list(group['clients'])

                return {'message': group}, 200
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def put(self, key, id):
        if key == KEY:
            data = argument.parse_args()
            group = GroupModel.search(id)
            if group and group.status != 'disabled':
                print(type(data['clients']))
                response = register_group_clients(data['clients'], id)
                if response == True:

                    # PROCESSO PARA ARMAZENAR NO SQLITE
                    data['clients'] = convert_string(data['clients'])
                    
                    try:
                        group.update(**data)
                        group.save()
                        return {'message': 'updated group'}, 200
                    except BaseException as error:
                        return {'message': f"Unexpected {error}, {type(error)}"}, 502
                return response
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def delete(self, key, id):
        if key == KEY:
            group = GroupModel.search(id)
            if group and group.status != 'disabled':
                response = disabled_group_clients(group.clients, id)
                if response == True:
                    data = {
                        "title": group.title,
                        "description": group.description,
                        "clients": group.clients,
                        "status": "disabled"
                    }
                    try:
                        group.update(**data)
                        group.save()
                        return {'message': 'group disabled'}, 200
                    except BaseException as error:
                        return {'message': f"Unexpected {error}, {type(error)}"}, 502
                return response
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401


# /API_KEY/groups
class Groups(Resource):
    @jwt_required()
    def get(self, key):
        if key == KEY:
            groups = [group.json() for group in GroupModel.query.all() if group.status != 'disabled']

            # PROCESSO PARA RETORNAR DO SQLITE
            for group in groups:
                group['clients'] = convert_list(group['clients'])

            return {'message': groups}, 200
        return {'message': 'unauthorized access'}, 401



def register_group_clients(clients, id):
    for client in clients:
        client = ClientModel.search(client)
        if client:
            # PROCESSO PARA RETORNAR DO SQLITE
            groups = convert_list(client.groups)
            ########
            if len(groups) == 0:
                data = {
                    'name': client.name,
                    'type': client.type,
                    'doc': client.doc,
                    'email': client.email,
                    'phone': client.phone,
                    'groups': str(id),
                    'api_key': client.api_key,
                    'api_secret': client.api_secret,
                    'status': client.status,
                }
                try:
                    client.update(**data)
                    client.save()
                except BaseException as error:
                    print(f"unexpected {error}, {type(error)}")
            group_contains = None
            for group in groups:
                if group == str(id):
                    group_contains = True
            if group_contains != True:
                groups.append(str(id))
                groups = convert_string(groups)
                data = {
                    'name': client.name,
                    'type': client.type,
                    'doc': client.doc,
                    'email': client.email,
                    'phone': client.phone,
                    'groups': groups,
                    'api_key': client.api_key,
                    'api_secret': client.api_secret,
                    'status': client.status,
                }
                try:
                    client.update(**data)
                    client.save()
                except BaseException as error:
                    print(f"unexpected {error}, {type(error)}")
    return True


def disabled_group_clients(clients, id):
    clients = convert_list(clients)
    for client in clients:
        client = ClientModel.search(client)
        if client:
            # PROCESSO PARA RETORNAR DO SQLITE
            groups = convert_list(client.groups)
            ########
            if len(groups) != 0:
                group_contains = False
                for group in groups:
                    if group == str(id):
                        group_contains = True
                if group_contains == True:
                    groups.remove(str(id))
                    groups = convert_string(groups)
                    data = {
                        'name': client.name,
                        'type': client.type,
                        'doc': client.doc,
                        'email': client.email,
                        'phone': client.phone,
                        'groups': groups,
                        'api_key': client.api_key,
                        'api_secret': client.api_secret,
                        'status': client.status,
                    }
                    try:
                        client.update(**data)
                        client.save()
                    except BaseException as error:
                        print(f"unexpected {error}, {type(error)}")
    return True