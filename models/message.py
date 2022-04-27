from config import database


class MessageModel(database.Model):
    __tablename__ = 'message'

    id = database.Column(database.String(36), primary_key=True)
    id_user = database.Column(database.String(36))
    id_chat = database.Column(database.String(36))
    text = database.Column(database.String(300))
    datetime = database.Column(database.String(20))
    status = database.Column(database.String(20))
    
    def __init__(self, id, id_user, id_chat, text, datetime, status):
        self.id = id
        self.id_user = id_user
        self.id_chat = id_chat
        self.text = text
        self.datetime = datetime
        self.status = status
    
    def json(self):
        return {
            'id': self.id,
            'id_user': self.id_user,
            'id_chat': self.id_chat,
            'text': self.text,
            'datetime': self.datetime,
            'status': self.status,
        }
    
    @classmethod
    def search(cls, id):
        message = cls.query.filter_by(id=id).first()
        if message:
            return message
        return None
    
    def save(self):
        database.session.add(self)
        database.session.commit()

    def update(self, status):
        self.status = status

    def delete(self):
        database.session.delete(self)
        database.session.commit()