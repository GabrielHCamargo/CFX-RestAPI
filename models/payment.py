import requests, json
from config import database, PUBLIC_KEY_EDUZZ, API_KEY_EDUZZ, EMAIL

URL = 'https://api2.eduzz.com'


class PaymentModel(database.Model):
    __tablename__ = 'payment'

    id = database.Column(database.String(36), primary_key=True)
    id_contract = database.Column(database.String(36))
    name = database.Column(database.String(100))
    doc = database.Column(database.String(40))
    email = database.Column(database.String(255))
    phone = database.Column(database.String(40))
    price = database.Column(database.String(40))
    status = database.Column(database.String(20))
    datetime = database.Column(database.String(20))
    

    def __init__(self, id, id_contract, name, doc, email, phone, price, status, datetime):
        self.id = id
        self.id_contract = id_contract
        self.name = name
        self.doc = doc
        self.email = email
        self.phone = phone
        self.price = price
        self.status = status
        self.datetime = datetime

    def json(self):
        return {
            'id': self.id,
            'id_contract': self.id_contract,
            'name': self.name,
            'doc': self.doc,
            'email': self.email,
            'phone': self.phone,
            'price': self.price,
            'status': self.status,
            'datetime': self.datetime,
        }
    
    @classmethod
    def search(cls, doc):
        payment = cls.query.filter_by(doc=doc).first()
        if payment:
            return payment
        return None
    
    def save(self):
        database.session.add(self)
        database.session.commit()
    
    def update(self, status):
        self.status = status

    def delete(self):
        database.session.delete(self)
        database.session.commit()



def authenticate():
    try:
        url = URL + '/credential/generate_token'
        payload={'publickey': PUBLIC_KEY_EDUZZ, 'apikey': API_KEY_EDUZZ, 'email': EMAIL}
        response = requests.request("POST", url, headers={}, data=payload, files={})
        return json.loads(response.text)['data']['token']
    except:
        return None


def product():
    try:
        url = URL + '/content/content_list'
        headers = {'Token': authenticate(), 'PublicKey': PUBLIC_KEY_EDUZZ, 'APIKey': API_KEY_EDUZZ}
        response = requests.request("GET", url, headers=headers, data={}, files={})
        products = []
        for product in json.loads(response.text)['data']:
            id = product['content_id']
            if id == 1274245 or id == 1274237 or id == 1274222:
                data = {
                    'id': product['content_id'], 
                    'title': product['title'], 
                    'price': product['recurrence_price'],
                    'url': 'https://sun.eduzz.com/' + str(product['content_id'])
                }
                products.append(data)
        return products
    except:
        return None


def contract(doc):
    try:
        url = URL + '/subscription/get_contract_list'
        headers = {'Token': authenticate(), 'PublicKey': PUBLIC_KEY_EDUZZ, 'APIKey': API_KEY_EDUZZ}
        response = requests.request("GET", url, headers=headers, data={}, files={})
        data = None
        for contract in json.loads(response.text)['data']:
            product = contract['product_id']
            if product == 1274245 or product == 1274237 or product == 1274222:
                if contract['client_document'] == doc:
                    data = {
                        'id': contract['contract_id'],
                        'status': contract['contract_status'],
                        'price': contract['payment_value'],
                        'date': contract['payment_last_date'],
                    }
        if data is not None:
            url = URL + '/subscription/' + str(data['id']) + '/client'
            headers = {'Token': authenticate(), 'PublicKey': PUBLIC_KEY_EDUZZ, 'APIKey': API_KEY_EDUZZ}
            response = requests.request("GET", url, headers=headers, data={}, files={})
            response = json.loads(response.text)['data']
            date = data['date'][0:16]
            data = {
                'id_contract': str(data['id']),
                'name': response[0]['company_name'],
                'doc': doc,
                'email': response[0]['email'],
                'phone': response[0]['cellphone'],
                'price': data['price'],
                'datetime': date,
                'status': data['status'],
            }
        return data
    except:
        None


def payment(start, end, doc):
    try:
        url = URL + '/sale/get_sale_list?start_date=' + start + '&end_date=' + end
        headers = {'Token': authenticate(), 'PublicKey': PUBLIC_KEY_EDUZZ, 'APIKey': API_KEY_EDUZZ}
        response = requests.request("GET", url, headers=headers, data={}, files={})
        for sale in json.loads(response.text)['data']:
            if sale['client_document'] == doc:
                return sale['sale_status_name']
            return None
    except:
        return None