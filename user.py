from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, name, age, gender, email, password, is_admin):
        self.username = username
        self.id=id
        self.name=name
        self.age=int(age.days/365.2425)
        self.gender=gender
        self.email=email
        self.password = password
        self.active = True
        self.is_admin = is_admin

    def get_id(self):
        return self.username

    @property
    def is_active(self):
        return self.active

class Comment:
    def __init__(self, id, content, game_id, user_id):
        self.id=id
        self.content=content
        self.user_id=user_id
        self.game_id=game_id
