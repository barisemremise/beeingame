from flask import Flask
from flask_login import LoginManager

import view
from game import gamebase
from view import get_user

lm= LoginManager()

@lm.user_loader
def load_user(user_id):
    return get_user(user_id)


def create_app():
    app=Flask(__name__)
    app.add_url_rule("/", view_func=view.home_page)
    app.add_url_rule("/insert_db", view_func=view.insert_db)
    app.add_url_rule("/new_game", view_func=view.new_game, methods=["GET", "POST"])
    app.add_url_rule("/login", view_func=view.login_page, methods=["GET","POST"])
    app.add_url_rule("/games", view_func=view.pgames_page, methods=["GET", "POST"])
    app.add_url_rule("/signup",view_func=view.signup_page, methods=["GET","POST"])
    app.add_url_rule("/warning",view_func=view.warning_page)
    app.add_url_rule("/user/<string:username>", view_func=view.user_page)
    app.add_url_rule("/game/<int:gameid>", view_func=view.game_page, methods=["GET","POST"])
    app.add_url_rule("/search",view_func=view.search_page,methods=["GET","POST"])
    app.add_url_rule("/settings", view_func=view.settings_page, methods=["GET","POST"])
    app.add_url_rule("/logout",view_func=view.logout)

    app.config.from_object("settings")
    
    lm.init_app(app)
    lm.login_view = "login_page"

    db = gamebase()
    view.connect_db()
    view.create_gamebase(db)
    app.config["db"]=db
    return app

if __name__ == "__main__":
    app=create_app()
    app.run(host="0.0.0.0", port=8080)
    view.close_db()

