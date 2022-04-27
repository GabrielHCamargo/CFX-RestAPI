from config import database


class PostModel(database.Model):
    __tablename__ = 'post'


    id = database.Column(database.String(36), primary_key=True)
    profile = database.Column(database.String(42))
    name = database.Column(database.String(100))
    media = database.Column(database.String(42))
    text = database.Column(database.String(300))
    datetime = database.Column(database.String(20))
    status = database.Column(database.String(20))
    

    def __init__(self, id, profile, name, media, text, datetime, status):
        self.id = id
        self.profile = profile
        self.name = name
        self.media = media
        self.text = text
        self.datetime = datetime
        self.status = status
    
    def json(self):
        return {
            'id': self.id,
            'profile': self.profile,
            'name': self.name,
            'media': self.media,
            'text': self.text,
            'datetime': self.datetime,
            'status': self.status, 
        }
    
    @classmethod
    def search(cls, id):
        post = cls.query.filter_by(id=id).first()
        if post:
            return post
        return None
    
    def save(self):
        database.session.add(self)
        database.session.commit()
    
    def update(self, media, text, status):
        self.media = media
        self.text = text
        self.status = status

    def delete(self):
        database.session.delete(self)
        database.session.commit()