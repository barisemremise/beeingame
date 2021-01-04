from flask import Flask
from flask import current_app
from flask_login import UserMixin
import datetime

x = datetime.datetime.now()

class User(UserMixin):
    def __init__(self, id, username, name, birth, gender, email, password):
        self.username = username
        self.id=id
        self.name=name
        self.age=x.year-birth
        self.gender=gender
        self.email=email
        self.password = password
        self.active = True

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