from flask_restful import Resource, reqparse
from models.client import ClientModel
from models.group import GroupModel
from models.user import UserModel
from flask_jwt_extended import jwt_required
from config import id_generator, convert_string, convert_list, KEY


argument = reqparse.RequestParser()
argument.add_argument('name', type=str)
argument.add_argument('type', type=str)
argument.add_argument('doc', type=str)
argument.add_argument('email', type=str)
argument.add_argument('phone', type=str)
argument.add_argument('groups', action='append')
argument.add_argument('api_key', type=str)
argument.add_argument('api_secret', type=str)
argument.add_argument('status', type=str)


# /API_KEY/client/register
class ClientRegister(Resource):
    @jwt_required()
    def post(self, key):
        if key == KEY:
            data = argument.parse_args()

            # PROCESSO PARA ARMAZENAR NO SQLITE
            data['groups'] = convert_string(data['groups'])


            id = id_generator(data['doc'])
            if ClientModel.search(str(id)) is None:
                data = {
                    'id': str(id),
                    'name': data['name'],
                    'type': data['type'],
                    'doc': data['doc'],
                    'email': data['email'],
                    'phone': data['phone'],
                    'groups':data['groups'],
                    'api_key': data['api_key'],
                    'api_secret': data['api_secret'],
                    'status': data['status'],
                }
                client = ClientModel(**data)
                try:
                    client.save()
                except BaseException as error:
                    return {'message': f"unexpected {error}, {type(error)}"}, 502

                # CRIAR USUÁRIO
                id_user = id_generator(data['email'])
                search_user = UserModel.search(str(id_user))
                if search_user is None:
                    user = {
                        'id': str(id_user),
                        'id_client': str(id),
                        'name': data['name'],
                        'doc': data['doc'],
                        'email': data['email'],
                        'password': data['phone'],
                        'status': 'activated',
                    }
                    user = UserModel(**user)
                    
                    try:
                        user.save()
                        return {'message': 'client and user created'}, 201
                    except BaseException as error:
                        client.delete()
                        return {'message': f"unexpected {error}, {type(error)}"}, 502

                elif search_user.password == None or search_user.password == '':
                    user = {
                        'id_client': str(id),
                        'name': data['name'],
                        'doc': data['doc'],
                        'email': data['email'],
                        'password': data['phone'],
                        'status': 'activated',
                    }                   
                    try:
                        search_user.update(**user)
                        search_user.save()
                        return {'message': 'client created and user updated'}, 201
                    except BaseException as error:
                        client.delete()
                        return {'message': f"unexpected {error}, {type(error)}"}, 502

                user = {
                    'id_client': str(id),
                    'name': search_user.name,
                    'doc': data['doc'],
                    'email': search_user.email,
                    'password': search_user.password,
                    'status': 'activated',
                }
                
                try:
                    search_user.update(**user)
                    search_user.save()
                except BaseException as error:
                    client.delete()
                    return {'message': f"unexpected {error}, {type(error)}"}, 502
                
                try:
                    response = register_clients_groups(data['groups'], str(id))
                    return {'message': 'client created and user updated'}, 201
                except BaseException as error:
                    client.delete()
                    return {'message': f"unexpected {error}, {type(error)}"}, 502

            return {'message': 'client already exist'}, 400
        return {'message': 'unauthorized access'}, 401


# /API_KEY/client/ID
class Client(Resource):
    @jwt_required()
    def get(self, key, id):
        if key == KEY:
            client = ClientModel.search(id)
            if client and client.status != 'disabled':
                client = client.json()

                # PROCESSO PARA RETORNAR DO SQLITE
                client['groups'] = convert_list(client['groups'])

                return {'message': client}, 200
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def put(self, key, id):
        if key == KEY:
            data = argument.parse_args()

            # PROCESSO PARA ARMAZENAR NO SQLITE
            data['groups'] = convert_string(data['groups'])

            client = ClientModel.search(id)
            if client and client.status != 'disabled':
                try:
                    client.update(**data)
                    client.save()
                    client = client.json()

                    # PROCESSO PARA RETORNAR DO SQLITE
                    client['groups'] = convert_list(client['groups'])

                    return {'message': 'updated client'}, 200
                except BaseException as error:
                    return {'message': f"unexpected {error}, {type(error)}"}, 502
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def delete(self, key, id):
        if key == KEY:
            client = ClientModel.search(id)
            if client and client.status != 'disabled':
                data = {
                    'name': client.name,
                    'type': client.type,
                    'doc': '',
                    'email': client.email,
                    'phone': client.phone,
                    'groups': client.groups,
                    'api_key': '',
                    'api_secret': '',
                    'status': 'disabled',
                }
                id_user = id_generator(client.email)
                search_user = UserModel.search(str(id_user))
                user = {
                    'id_client': None,
                    'name': search_user.name,
                    'doc': '',
                    'email': search_user.email,
                    'password': '',
                    'status': 'disabled',
                }
                try:
                    client.update(**data)
                    search_user.update(**user)
                    client.save()
                    search_user.save()
                    return {'message': 'client disabled'}, 200
                except BaseException as error:
                    return {'message': f"unexpected {error}, {type(error)}"}, 502
            return {'message': 'id not found'}, 404
        return {'message': 'unauthorized access'}, 401


# /API_KEY/clients
class Clients(Resource):
    @jwt_required()
    def get(self, key):
        if key == KEY:
            clients = [client.json() for client in ClientModel.query.all() if client.status != 'disabled']

            # PROCESSO PARA RETORNAR DO SQLITE
            for client in clients:
                client['groups'] = convert_list(client['groups'])

            return {'message': clients}, 200
        return {'message': 'unauthorized access'}, 401


# /API_KEY/client/keys/ID
class ClientKeys(Resource):
    @jwt_required()
    def get(self, key, id):
        if key == KEY:
            client = ClientModel.keys(id)
            if client and client.status != 'disabled':
                return {'message': 'keys ok'}, 200
            return {'message': 'keys not found'}, 404
        return {'message': 'unauthorized access'}, 401


# /API_KEY/client/document
class ClientDocument(Resource):
    @jwt_required()
    def post(self, key):
        if key == KEY:
            data = argument.parse_args()
            id = id_generator(data['doc'])
            client = ClientModel.search(str(id))
            if client and client.status != 'disabled':
                return {'message': 'doc ok'}, 200
            return {'message': 'doc not found'}, 404
        return {'message': 'unauthorized access'}, 401




def register_clients_groups(groups, id):
    for group in groups:
        group = GroupModel.search(group)
        if group:
            # PROCESSO PARA RETORNAR DO SQLITE
            clients = convert_list(group.clients)
            ########
            if len(clients) == 0:
                #title, description, clients, status
                data = {
                    'title': group.name,
                    'description': group.type,
                    'clients': str(id),
                    'status': group.email,
                }
                try:
                    group.update(**data)
                    group.save()
                except BaseException as error:
                    print(f"unexpected {error}, {type(error)}")
            client_contains = None
            for client in clients:
                if client == str(id):
                    client_contains = True
            if client_contains != True:
                clients.append(str(id))
                clients = convert_string(clients)
                data = {
                    'title': group.name,
                    'description': group.type,
                    'clients': clients,
                    'status': group.email,
                }
                try:
                    group.update(**data)
                    group.save()
                except BaseException as error:
                    print(f"unexpected {error}, {type(error)}")
    return True