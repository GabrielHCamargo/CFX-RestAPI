from config import database


class ClientModel(database.Model):
    __tablename__ = 'client'

    id = database.Column(database.String(36), primary_key=True)
    name = database.Column(database.String(100))
    type = database.Column(database.String(2))
    doc = database.Column(database.String(14))
    email = database.Column(database.String(255))
    phone = database.Column(database.String(40))
    groups = database.Column(database.String(8200))
    api_key = database.Column(database.String(80))
    api_secret = database.Column(database.String(80))
    status = database.Column(database.String(20))

    def __init__(self, id, name, type, doc, email, phone, groups, api_key, api_secret, status):
        self.id = id
        self.name = name
        self.type = type
        self.doc = doc
        self.email = email
        self.phone = phone
        self.groups = groups
        self.api_key = api_key
        self.api_secret = api_secret
        self.status = status
    
    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'email': self.email,
            'phone': self.phone,
            'groups': self.groups,
            'status': self.status,
        }
   
    
    @classmethod
    def search(cls, id):
        client = cls.query.filter_by(id=id).first()
        if client:
            return client
        return None


    @classmethod
    def keys(cls, id):
        client = cls.query.filter_by(id=id).first()
        if client:
            if client.api_key and client.api_secret:
                return client
        return None
    

    @classmethod
    def client(cls, email):
        client = cls.query.filter_by(email=email).first()
        if client and client.status != 'disabled':
            return client.id
        return None


    def save(self):
        database.session.add(self)
        database.session.commit()


    def update(self, name, type, doc, email, phone, groups, api_key, api_secret, status):
        self.name = name
        self.type = type
        self.doc = doc
        self.email = email
        self.phone = phone
        self.groups = groups
        self.api_key = api_key
        self.api_secret = api_secret
        self.status = status


    def delete(self):
        database.session.delete(self)
        database.session.commit()