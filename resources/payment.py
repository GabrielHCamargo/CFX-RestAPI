from datetime import datetime
from config import id_generator, KEY
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from models.payment import PaymentModel, product, contract, payment


argument = reqparse.RequestParser()
argument.add_argument('doc', type=str)


class Payment(Resource):
    def get(self, key, id):
        if key == KEY:
            if id == 'create':
                return {'message': product()}, 200
            return {'message': 'check your request'}, 409
        return {'message': 'unauthorized access'}, 401

    @jwt_required()
    def post(self, key, id):
        if key == KEY:
            if id == 'contract':
                data = argument.parse_args()
                pay = PaymentModel.search(data['doc'])
                if pay is None:
                    response = contract(data['doc'])
                    if response is not None:
                        id = id_generator(str(response['id_contract']))
                        pay = PaymentModel(str(id), **response)
                        pay.save()
                        return {'message': pay.json()}, 200
                    return {'message': 'contract not found'}, 404
                response = contract(data['doc'])
                pay.update(response['status'])
                pay.save()
                return {'message': pay.json()}, 200

            elif id == 'status':
                data = argument.parse_args()
                end = datetime.today().strftime('%Y-%m-%d')
                start = datetime.today().strftime('%Y-%m-01')
                response = payment(start, end, data['doc'])
                if response is not None:
                    return {'message': response}, 200
                return {'message': 'payment not found'}, 404
            return {'message': 'check your request'}, 409
        return {'message': 'unauthorized access'}, 401
