import profile
from config import database

class AdminModel(database.Model):
    __tablename__ = 'admin'

    id = database.Column(database.String(36), primary_key=True)
    name = database.Column(database.String(100))
    login = database.Column(database.String(40))
    email = database.Column(database.String(255))
    password = database.Column(database.String(40))
    profile = database.Column(database.String(42))
    status = database.Column(database.String(20))

    def __init__(self, id, name, login, email, password, profile, status):
        self.id = id
        self.name = name
        self.login = login
        self.email = email
        self.password = password
        self.profile = profile
        self.status = status
    
    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'login': self.login,
            'email': self.email,
            'profile': self.profile,
            'status': self.status,
        }
    
    @classmethod
    def search(cls, id):
        admin = cls.query.filter_by(id=id).first()
        if admin:
            return admin
        return None
    
    def save(self):
        database.session.add(self)
        database.session.commit()

    def update(self, profile, status):
        self.profile = profile
        self.status = status
        
    def delete(self):
        database.session.delete(self)
        database.session.commit()