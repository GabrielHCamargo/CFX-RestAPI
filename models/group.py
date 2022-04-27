from config import database


class GroupModel(database.Model):
    __tablename__ = 'group'

    id = database.Column(database.String(36), primary_key=True)
    title = database.Column(database.String(40))
    description = database.Column(database.String(100))
    clients = database.Column(database.String(8200))
    status = database.Column(database.String(20))
    
    def __init__(self, id, title, description, clients, status):
        self.id = id
        self.title = title
        self.description = description
        self.clients = clients
        self.status = status
    
    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'clients': self.clients,
            'status': self.status
        }
    
    @classmethod
    def search(cls, id):
        group = cls.query.filter_by(id=id).first()
        if group:
            return group
        return None
    
    def save(self):
        database.session.add(self)
        database.session.commit()
    
    def update(self, title, description, clients, status):
        self.title = title
        self.description = description
        self.clients = clients
        self.status = status

    def delete(self):
        database.session.delete(self)
        database.session.commit()