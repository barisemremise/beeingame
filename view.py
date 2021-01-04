from flask.helpers import flash, url_for

from user import User, Comment
from flask import render_template, current_app, abort, redirect
from flask.globals import request
from flask_login import current_user, login_user, logout_user
from passlib.hash import pbkdf2_sha256 as hasher
from operator import itemgetter
from game import Game
import psycopg2

def connect_db():
    global connection
    connection = psycopg2.connect(user="postgres",
                                  password="baris.7200",
                                  database="beeingame")

    global cursor
    cursor = connection.cursor()

def close_db():
    cursor.close()
    connection.close()

def home_page():
    query='''SELECT username FROM users ORDER BY user_id'''
    cursor.execute(query)
    record=cursor.fetchall()
    users=[x[0] for x in record]
    
    return render_template("home.html",users=users)

def settings_page():

    if request.method=="GET":
        query='''SELECT list_name FROM likelist WHERE user_id=%s'''
        cursor.execute(query,(current_user.id,))
        listname=cursor.fetchone()[0]
        return render_template("settings.html",listname=listname)
    else:
        if 'change_name' in request.form:
            new_name=request.form['change_name']
            query='''UPDATE users SET name=%s WHERE user_id=%s'''
            cursor.execute(query,(new_name,current_user.id))
            connection.commit()
        
        elif 'change_email' in request.form:
            new_email=request.form['change_email']
            query='''UPDATE users SET email=%s WHERE user_id=%s'''
            cursor.execute(query,(new_email,current_user.id))
            connection.commit()
        
        elif 'change_password' in request.form:
            new_passord=hash_password(request.form['change_password'])
            query='''UPDATE users SET user_password=%s WHERE user_id=%s'''
            cursor.execute(query,(new_passord,current_user.id))
            connection.commit()

        elif 'change_list' in request.form:
            new_name=request.form['change_list']
            query='''UPDATE likelist SET list_name=%s WHERE user_id=%s'''
            cursor.execute(query,(new_name,current_user.id))
            connection.commit()

        elif 'delete' in request.form:
            query='''UPDATE likelist SET list_name=Null WHERE user_id=%s'''
            cursor.execute(query,(current_user.id,))
            connection.commit()
            
        return redirect(url_for('user_page',username=current_user.username))
def login_page():
    if request.method=="GET":
        return render_template("login.html")
    else:
        if len(request.form['username']) and len(request.form['password']):
            username=request.form['username']
            password=request.form['password']
            query='''SELECT username FROM users WHERE username=%s'''
            cursor.execute(query, (username,))
            usercontrol=cursor.fetchone()
            if usercontrol is not None:
                user=get_user(username)
                if hasher.verify(password, user.password):
                    login_user(user)
                    flash("You have logged in.")
                    next_page = request.args.get("next", url_for("home_page"))
                    return redirect(next_page)
        return redirect(url_for('login_page'))

def signup_page():
    if request.method=="GET":
        return render_template("signup.html")
    else:
        if len(request.form['name']) and len(request.form['username']) and len(request.form['email']) and len(request.form['year']) and len(request.form['password']):
            name=request.form['name']
            username=request.form['username']
            email=request.form['email']
            birtyear=request.form['year']
            gender=request.form['gender']
            password=hash_password(request.form['password'])
            control='''SELECT username FROM users WHERE username=%s OR email=%s'''
            cursor.execute(control,(username, email))
            user_=cursor.fetchone()
            if user_:
                return redirect(url_for('signup_page'))
            else:
                query='''INSERT INTO users(username, name, birthyear, gender, email, user_password)
                VALUES (%s, %s, %s, %s, %s, %s)'''
                cursor.execute(query,(username, name, birtyear, gender, email, password))
                connection.commit()
                query='''INSERT INTO likelist(user_id) VALUES ((SELECT user_id FROM users WHERE username=%s))'''
                cursor.execute(query,(username,))
                connection.commit()
                return render_template("login.html")
        else:
            return redirect(url_for('signup_page'))

def logout():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for('home_page'))

def pgames_page():
    db = current_app.config["db"]
    if request.method=="GET":
        create_gamebase(db)
        games = db.get_gamelist()
        return render_template("pgames.html",games=games, title="Most Popular Games")
    elif request.method=="POST":
        mode="game_mode="
        price="("
        age="("
        genre="("
        if request.form.getlist('mode'):
            if len(request.form.getlist('mode'))==2:
                mode=mode+"'MS'"
            else:
                mode=mode+"'"+request.form['mode']+"'"
        if request.form.getlist('price'):
            pricenum=len(request.form.getlist('price'))
            if pricenum!=3:
                for i in request.form.getlist('price'):
                    if i=='1' and pricenum>1:
                        price=price+"price<50 OR "
                        pricenum -= 1
                    elif i=='1' and pricenum==1:
                        price=price+"price<50"
                    elif i=='2' and pricenum>1:
                        price=price+"(price>=50 AND price<100) OR "
                        pricenum -= 1
                    elif i=='2' and pricenum==1:
                        price=price+"(price>=50 AND price<100)"
                    elif i=='3':
                        price=price+"price>=100"
                price=price+")"
        if request.form.getlist('age'):
            agenum=len(request.form.getlist('age'))
            ages=request.form.getlist('age')
            if agenum!=5:
                if '3' in ages and agenum>1:
                    age=age+"age_rate=3 OR "
                    agenum -= 1
                elif '3' in ages and agenum==1:
                    age=age+"age_rate=3"
                if '7' in ages and agenum>1:
                    age=age+"age_rate=7 OR "
                    agenum -= 1
                elif '7' in ages and agenum==1:
                    age=age+"age_rate=7"
                if '12' in ages and agenum>1:
                    age=age+"age_rate=12 OR "
                    agenum -= 1
                elif '12' in ages and agenum==1:
                    age=age+"age_rate=12"
                if '16' in ages and agenum>1:
                    age=age+"age_rate=16 OR "
                    agenum -= 1
                elif '16' in ages and agenum==1:
                    age=age+"age_rate=16"
                if '18' in ages:
                    age=age+"age_rate=18"
                age=age+")"
        if request.form.getlist('genre'):
            for i in request.form.getlist('genre'):
                genre=genre+"genre_name="+"'"+i+"'"+" OR "
            genre=genre[:len(genre)-4]+")"
        query=""
        if genre!="(":
            query="SELECT game.game_id FROM game,genres, game_genre_rel WHERE genres.genre_id=game_genre_rel.genre_id AND game.game_id=game_genre_rel.game_id AND"
            query=" ".join((query,genre))
            query=query+"AND "
        else:
            query="SELECT game_id FROM game WHERE "
        if mode!="game_mode=":
            query=" ".join((query,mode))
            query=query+"AND "
        if price!="(":
            query=" ".join((query,price))
            query=query+"AND "
        if age!="(":
            query=" ".join((query,age))
            query=query+"AND "
        query=query[:len(query)-4]
        cursor.execute(query)
        record=cursor.fetchall()
        games=[]
        counter=0
        for id in record:
            game=create_game(id[0])
            counter+=1
            games.append((counter,game))
        games.sort(key=itemgetter(1),reverse=True)
        return render_template("pgames.html",games=games,title="Games By Filter")

def warning_page():
    return render_template("warning.html")

def user_page(username):
    query='''SELECT list_id, list_name FROM likelist inner join users ON likelist.user_id=users.user_id WHERE users.username=%s'''
    cursor.execute(query,(username,))
    record=cursor.fetchone()
    query='''SELECT game_id FROM list_game_rel WHERE list_id=%s'''
    cursor.execute(query,(record[0],))
    gamelist=cursor.fetchall()
    games=[]
    counter=0
    for id in gamelist:
        game=create_game(id[0])
        counter+=1
        games.append((counter,game))
        games.sort(key=itemgetter(1),reverse=True)
    user=get_user(username)
    return render_template("user.html",games=games,user=user,listname=record[1])

def game_page(gameid):
    db = current_app.config["db"]
    game=db.get_game(gameid)
    comments=create_comment_list(gameid)
    if current_user.is_active:
        likes=create_likelist(current_user.id)
    else:
        likes=[]
    if request.method=="GET":
        if game is None:
            abort(404)
        return render_template("game.html", game=game, gameid=gameid, comments=comments, likes=likes)
    elif 'like' in request.form or 'dislike' in request.form:
        if 'like' in request.form:
            update_like(game.id)
            if current_user.is_active:
                add_likelist(game.id, current_user.id)
                likes=create_likelist(current_user.id)
            else:
                likes=[]
        elif 'dislike' in request.form:
            update_dislike(game.id)
        create_gamebase(db)
        game=db.get_game(gameid)
        return render_template("game.html", game=game, gameid=gameid, comments=comments, likes=likes)
    elif 'comment' in request.form and 'commentsuser' in request.form:
        comment=request.form['comment']
        commentuser=request.form['commentsuser']
        if commentuser==current_user.username:
            user_id='''SELECT user_id FROM users WHERE username=%s'''
            cursor.execute(user_id,(commentuser, ))
            user_id=cursor.fetchone()[0]
            query='''INSERT INTO comments(content, game_id, user_id)
            VALUES (%s, %s, %s)'''
            cursor.execute(query,(comment, gameid, user_id))
            connection.commit()
            comments=create_comment_list(gameid)
        return render_template("game.html", game=game, gameid=gameid, comments=comments, likes=likes)
    elif 'update' in request.form:
        update=request.form['update']
        commentid=request.form['commentup']

        query='''UPDATE comments SET content=%s WHERE comment_id=%s'''
        cursor.execute(query,(update,commentid))
        connection.commit()
        create_comment_list(gameid)
        return redirect(url_for('game_page',gameid=gameid))
    elif 'delete' in request.form:
        query='''DELETE FROM comments WHERE comment_id=%s'''
        cursor.execute(query,(request.form['delete'],))
        connection.commit()
        create_comment_list(gameid)
        return redirect(url_for('game_page',gameid=gameid))
    
    elif 'remove_game' in request.form:
        query='''DELETE FROM list_game_rel WHERE game_id=%s AND list_id=(SELECT list_id FROM likelist WHERE user_id=%s)'''
        cursor.execute(query,(gameid,current_user.id))
        connection.commit()

        query='''UPDATE game SET likes=likes-1 WHERE game_id=%s'''
        cursor.execute(query,(gameid,))
        connection.commit()
        return redirect(url_for('user_page',username=current_user.username))
    if game is None:
        abort(404)
    return render_template("game.html", game=game, gameid=gameid, comments=comments, likes=likes)

def search_page():
    if request.method=="POST":
        search=request.form['search']
        query="SELECT game_id FROM game WHERE game_name ILIKE '%"+search+"%'"
        cursor.execute(query)
        record=cursor.fetchall()
        games=[]
        for id in record:
            game=create_game(id[0])
            games.append(game)
            games.sort(reverse=True)
        return render_template("search.html",games=games,title="Search Results for {}".format(search))

    return render_template("search.html")

def update_like(id):
    query='''UPDATE game SET likes=likes+1 WHERE game_id=%s'''
    cursor.execute(query,(id,))
    connection.commit()

def update_dislike(id):

    query='''UPDATE game SET dislikes=dislikes+1 WHERE game_id=%s'''
    cursor.execute(query,(id, ))
    connection.commit()

def create_gamebase(db):

    db.clear_games()
    number='''SELECT COUNT(*) FROM game;'''
    cursor.execute(number)
    total_game_number=cursor.fetchone()
    for game_id in range(1,total_game_number[0]+1):   
        db.add_game(create_game(game_id))

def create_game(game_id):
    query='''SELECT * FROM game WHERE game_id=%s'''
    cursor.execute(query,(game_id, ))
    record=cursor.fetchone()
    company='''SELECT company.company_name FROM game right join company on company.company_id=game.company_id WHERE game.game_id=%s'''
    cursor.execute(company,(game_id, ))
    company_name=cursor.fetchone()[0]
    genre='''SELECT genres.genre_name FROM genres right join game_genre_rel on genres.genre_id=game_genre_rel.genre_id 
    WHERE game_genre_rel.game_id=%s;'''
    cursor.execute(genre,(game_id, ))
        
    genres=[x[0] for x in cursor.fetchall()]
        
    game=Game(record[0],record[1],record[2],company_name,record[4],record[5],genres,record[6],record[7],record[8],record[9])
    return game

def hash_password(password):
    hashed=hasher.hash(password)
    return hashed

def get_user(username):
    query='''SELECT * FROM users WHERE username=%s'''
    cursor.execute(query, (username,))
    record=cursor.fetchone()
    user=User(record[0],record[1],record[2],record[3],record[4],record[5],record[6])

    return user

def create_comment_list(gameid):
    query='''SELECT * FROM comments WHERE game_id=%s ORDER BY comment_id'''
    cursor.execute(query,(gameid,))
    record=cursor.fetchall()

    comments=[]
    for i in record:
        comment=Comment(i[0],i[1],i[2],i[3])
        query='''SELECT * FROM users WHERE user_id=%s'''
        cursor.execute(query,(i[3], ))
        userdata=cursor.fetchone()
        user=User(userdata[0],userdata[1],userdata[2],userdata[3],userdata[4],userdata[5],userdata[6])
        comments.append((user,comment))
    return comments

def add_likelist(gameid,userid):
    query='''INSERT INTO list_game_rel(list_id, game_id)
    VALUES ((SELECT list_id FROM likelist WHERE user_id=%s),%s)'''
    cursor.execute(query,(userid, gameid))
    connection.commit()

def create_likelist(userid):
    query='''SELECT game.game_id FROM list_game_rel, game, likelist WHERE likelist.list_id=list_game_rel.list_id 
    AND game.game_id=list_game_rel.game_id AND likelist.user_id=%s;'''
    cursor.execute(query,(userid,))
    record=cursor.fetchall()

    games=[]
    for id in record:
        games.append(id[0])
    return games