from config import database


class ChatModel(database.Model):
    __tablename__ = 'chat'

    id = database.Column(database.String(36), primary_key=True)
    title = database.Column(database.String(40))
    cover = database.Column(database.String(42))
    users = database.Column(database.String(8200))
    status = database.Column(database.String(20))
    

    def __init__(self, id, title, cover, users, status):
        self.id = id
        self.title = title
        self.cover = cover
        self.users = users
        self.status = status
    
    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'cover': self.cover,
            'users': self.users,
            'status': self.status,
        }
    
    @classmethod
    def search(cls, id):
        chat = cls.query.filter_by(id=id).first()
        if chat:
            return chat
        return None
    
    def save(self):
        database.session.add(self)
        database.session.commit()
    
    def update(self, title, cover, users, status):
        self.title = title
        self.cover = cover
        self.users = users
        self.status = status

    def delete(self):
        database.session.delete(self)
        database.session.commit()