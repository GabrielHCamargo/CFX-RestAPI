from config import database



class UserModel(database.Model):
    __tablename__ = 'user'

    id = database.Column(database.String(36), primary_key=True)
    id_client = database.Column(database.String(36))
    name = database.Column(database.String(100))
    doc = database.Column(database.String(14))
    email = database.Column(database.String(255))
    password = database.Column(database.String(40))
    status = database.Column(database.String(20))

    def __init__(self, id, id_client, name, doc, email, password, status):
        self.id = id
        self.id_client = id_client
        self.name = name
        self.doc = doc
        self.email = email
        self.password = password
        self.status = status
    
    def json(self):
        return {
            'id': self.id,
            'id_client': self.id_client,
            'name': self.name,
            'email': self.email,
            'status': self.status,
        }

    
    @classmethod
    def search(cls, id):
        user = cls.query.filter_by(id=id).first()
        if user:
            return user
        return None  


    def save(self):
        database.session.add(self)
        database.session.commit()


    def update(self, id_client, name, doc, email, password, status):
        self.id_client = id_client
        self.name = name
        self.doc = doc
        self.email = email
        self.password = password
        self.status = status


    def delete(self):
        database.session.delete(self)
        database.session.commit()