from flask.helpers import flash, url_for

from flask import render_template, current_app, abort, redirect
from flask.globals import request
from flask_login import current_user, login_user, logout_user
from passlib.hash import pbkdf2_sha256 as hasher
from operator import itemgetter
from queries import *

def home_page():
    query='''SELECT username FROM users ORDER BY user_id'''
    cursor.execute(query)
    record=cursor.fetchall()
    users=[x[0] for x in record]
    
    return render_template("home.html",users=users)

def companies_page():
    complist=create_complist()
    return render_template("companies.html", complist=complist)

def company_page(id):
    company=create_company(id)
    games=create_gamelist_company(id)
    return render_template("company.html", company=company,games=games)

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
        
        elif 'delete_acc' in request.form:
            userid=current_user.id
            logout_user()
            query='''DELETE FROM users WHERE user_id=%s'''
            cursor.execute(query,(userid,))
            connection.commit()
            return redirect(url_for('home_page'))
            
        return redirect(url_for('user_page',username=current_user.username))
def login_page():
    if request.method=="GET":
        return render_template("login.html")
    else:
        message=""
        if 'username' in request.form and 'password' in request.form:
            username=request.form['username']
            password=request.form['password']
            if username and password:
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
                    else:
                        message="Wrong password!"
                else:
                    message="Wrong username!"
            else:
                message="Fill in required fields!"
        return render_template("login.html",message=message)

def signup_page():
    if request.method=="GET":
        return render_template("signup.html")
    else:
        if 'name' in request.form and 'username' in request.form and 'email' in request.form and 'year' in request.form and 'password' in request.form:
            name=request.form['name']
            username=request.form['username']
            email=request.form['email']
            birtyear=request.form['year']
            gender=request.form['gender']
            password=hash_password(request.form['password'])
            if name and username and email and birtyear and gender and password:
                control='''SELECT username FROM users WHERE username=%s OR email=%s'''
                cursor.execute(control,(username, email))
                user_=cursor.fetchone()
                if user_:
                    message="Username is not available!"
                    return render_template('signup.html',message=message)
                else:
                    query='''INSERT INTO users(username, name, birth, gender, email, user_password)
                    VALUES (%s, %s, %s, %s, %s, %s)'''
                    cursor.execute(query,(username, name, birtyear, gender, email, password))
                    connection.commit()
                    query='''INSERT INTO likelist(user_id) VALUES ((SELECT user_id FROM users WHERE username=%s))'''
                    cursor.execute(query,(username,))
                    connection.commit()

                    if username=='barisemremise':
                        query='''UPDATE users SET is_admin=True WHERE username=%s'''
                        cursor.execute(query(username,))
                        connection.commit()
                    return render_template("login.html")
            else:
                message="Fill in required fields!"
                return render_template("signup.html",message=message)
        else:
            message="Fill in required fields!"
            return render_template("signup.html",message=message)

def logout():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for('home_page'))

def pgames_page():
    db = current_app.config["db"]
    genre_list=create_genrelist()
    if request.method=="GET":
        create_gamebase(db)
        games = db.get_gamelist()
        return render_template("pgames.html",games=games, genre_list=genre_list, title="Most Popular Games")
    
    elif request.method=="POST":
        query="("
        if 'mode' in request.form and len(request.form.getlist('mode'))==1:
            mode=request.form['mode']
            query=query+"SELECT game.game_id, game.likes, game.dislikes, game.game_name FROM game WHERE game_mode='MS' UNION SELECT game.game_id, game.likes, game.dislikes, game.game_name FROM game WHERE game_mode='"+mode+"')"

        if 'price' in request.form and len(request.form.getlist('price'))<3:
            pricenum=len(request.form.getlist('price'))
            if query!="(":
                query=query+" INTERSECT ("
            for i in request.form.getlist('price'):
                if i=="above":
                    query=query+"SELECT game.game_id, game.likes, game.dislikes, game.game_name FROM game WHERE price>=100"
                elif i=="0-50":
                    query=query+"SELECT game.game_id, game.likes, game.dislikes, game.game_name FROM game WHERE price<50"
                else:
                    query=query+"SELECT game.game_id, game.likes, game.dislikes, game.game_name FROM game WHERE price>=50 AND price<100"
                pricenum-=1
                if pricenum:
                    query=query+" UNION "
            query=query+")"
        if 'age' in request.form and len(request.form.getlist('price'))<5:
            if query!="(":
                query=query+" INTERSECT ("
            agenum=len(request.form.getlist('age'))
            for i in request.form.getlist('age'):
                query=query+"SELECT game.game_id, game.likes, game.dislikes, game.game_name FROM game WHERE age_rate="+i
                agenum-=1
                if agenum:
                    query=query+" UNION "
            query=query+")"
        if 'genre' in request.form:
            if query!="(":
                query=query+" INTERSECT ("
            genrenum=len(request.form.getlist('genre'))
            for i in request.form.getlist('genre'):
                query=query+"SELECT game.game_id, game.likes, game.dislikes, game.game_name FROM game_genre_rel INNER JOIN genres ON genres.genre_id=game_genre_rel.genre_id INNER JOIN game ON game.game_id =game_genre_rel.game_id WHERE genres.genre_name='"+i+"'"
                genrenum-=1
                if genrenum:
                    query=query+" INTERSECT "
            query=query+")"
        if query!="(":
            query=query+" ORDER BY likes DESC, dislikes ASC, game_name ASC"
            cursor.execute(query)
            record=cursor.fetchall()
            games=[]
            for id in record:
                game=create_game(id[0])
                games.append((game.id,game))
            games.sort(key=itemgetter(1),reverse=True)
            return render_template("pgames.html",games=games, genre_list=genre_list, title="Games By Filter")
        else:
            return redirect(url_for('pgames_page'))

def warning_page():
    return render_template("warning.html")

def new_game():
    genres=create_genrelist()
    if request.method=="GET":
        return render_template("add_game.html", genres=genres)
    else:
        if 'name' in request.form and 'price' in request.form and 'company' in request.form and ('genre' in request.form or 'genre_add' in request.form) and 'age' in request.form and 'mode' in request.form and 'trailer' in request.form and 'info' in request.form:
            query='''SELECT game_id FROM game WHERE game_name=%s'''
            cursor.execute(query,(request.form['name'],))
            if cursor.fetchone() is None:
                name=request.form['name']
                price=float(request.form['price'])
                company=request.form['company']
                age=int(request.form['age'])
                if len(request.form.getlist('mode'))==2:
                    mode='MS'
                else:
                    mode=request.form['mode']
                trailer=request.form['trailer']
                info=request.form['info']

                query='''SELECT company_id FROM company WHERE company_name=%s'''
                cursor.execute(query,(company,))
                a=cursor.fetchone()

                if a is None:
                    query='''INSERT INTO company(company_name) VALUES (%s)'''
                    cursor.execute(query,(company,))
                    connection.commit()
                    query='''SELECT company_id FROM company WHERE company_name=%s'''
                    cursor.execute(query,(company,))
                    company=cursor.fetchone()[0]
                else:
                    company=a
                
                query='''INSERT INTO game(game_name, price, company_id, age_rate, game_mode, trailer, game_info)
                VALUES (%s, %s, %s, %s, %s, %s, %s)'''
                cursor.execute(query,(name, price, company, age, mode, trailer, info))
                connection.commit()
                
                if request.form.getlist('genre'):
                    for i in request.form.getlist('genre'):
                        query='''INSERT INTO game_genre_rel(game_id, genre_id) VALUES
                        ((SELECT game_id FROM game WHERE game_name=%s),(SELECT genre_id FROM genres WHERE genre_name=%s))'''
                        cursor.execute(query,(name, i))
                        connection.commit()
                if request.form['genre_add']:
                    addlist=[x.strip().capitalize() for x in request.form['genre_add'].split(',')]
                    for i in addlist:
                        if i not in genres:
                            query='''INSERT INTO genres(genre_name) VALUES (%s)'''
                            cursor.execute(query,(i,))
                            connection.commit()
                            query='''INSERT INTO game_genre_rel(game_id, genre_id)
                            VALUES((SELECT game_id FROM game WHERE game_name=%s),(SELECT genre_id FROM genres WHERE genre_name=%s))'''
                            cursor.execute(query,(name,i))
                            connection.commit()
                query='''SELECT game_id FROM game WHERE game_name=%s'''
                cursor.execute(query,(name,))
                gameid=cursor.fetchone()[0]
                db = current_app.config["db"]
                db.add_game(create_game(gameid))
                return redirect(url_for('game_page',gameid=gameid))
            else:
                message="Game already exists!"
                return render_template("add_game.html", genres=genres,message=message)   
        else:
            message="Fill in required fields!"
            return render_template("add_game.html", genres=genres,message=message)

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
    if request.method=="GET":
        user=get_user(username)
        return render_template("user.html",games=games,user=user,listname=record[1])
    else:
        if 'madmin' in request.form:
            update_admin(username,True)
        elif 'dadmin' in request.form:
            update_admin(username,False)
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
        db.delete_game(gameid)
        game=create_game(gameid)
        db.add_game(game)
        return render_template("game.html", game=game, gameid=gameid, comments=comments, likes=likes)
    elif 'delete_game' in request.form:
        delete_game(gameid)
        company_control(game.company)
        genre_control()
        return redirect(url_for('pgames_page'))
    elif 'comment' in request.form:
        comment=request.form['comment']
        commentuser=current_user.id
        query='''INSERT INTO comments(content, game_id, user_id)
        VALUES (%s, %s, %s)'''
        cursor.execute(query,(comment, gameid, commentuser))
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
    
    elif 'remove_gamelist' in request.form:
        query='''DELETE FROM list_game_rel WHERE game_id=%s AND list_id=(SELECT list_id FROM likelist WHERE user_id=%s)'''
        cursor.execute(query,(gameid,current_user.id))
        connection.commit()

        query='''UPDATE game SET likes=likes-1 WHERE game_id=%s'''
        cursor.execute(query,(gameid,))
        connection.commit()
        db.delete_game(gameid)
        db.add_game(create_game(gameid))
        return redirect(url_for('user_page',username=current_user.username))
    if game is None:
        abort(404)
    return render_template("game.html", game=game, gameid=gameid, comments=comments, likes=likes)

def search_page():
    if request.method=="POST":
        if len(request.form['search']):
            search=request.form['search']
            query="SELECT game_id FROM game WHERE game_name ILIKE '%"+search+"%' ORDER BY likes DESC, dislikes ASC, game_name ASC"
            cursor.execute(query)
            record=cursor.fetchall()
            games=[]
            for id in record:
                game=create_game(id[0])
                games.append(game)
                games.sort(reverse=True)
            
            query="SELECT company_id FROM company WHERE company_name ILIKE '%"+search+"%' ORDER BY company_name"
            cursor.execute(query)
            record=cursor.fetchall()
            companies=[]
            for id in record:
                company=create_company(id[0])
                companies.append(company)
            return render_template("search.html",games=games,companies=companies,title="Search Results for {}".format(search))

    return redirect(url_for('pgames_page'))

def updatecom_page(id):
    if request.method=="GET":
        company=create_company(id)
        return render_template("update_company.html", company=company)
    else:
        if 'delete_com' in request.form:
            query='''DELETE FROM company WHERE company_id=%s'''
            cursor.execute(query,(id,))
            connection.commit()
            genre_control()
            return redirect(url_for('companies_page'))
        elif 'name' in request.form:
            name=request.form['name']
            query='''UPDATE company SET company_name=%s WHERE company_id=%s'''
            cursor.execute(query, (name,id))
            connection.commit()
        elif 'ceo' in request.form:
            ceo=request.form['ceo']
            query='''UPDATE company SET ceo_name=%s WHERE company_id=%s'''
            cursor.execute(query, (ceo,id))
            connection.commit()
        elif 'year' in request.form:
            year=request.form['year']
            query='''UPDATE company SET year=%s WHERE company_id=%s'''
            cursor.execute(query, (year,id))
            connection.commit()
        elif 'country' in request.form:
            country=request.form['country']
            query='''UPDATE company SET country=%s WHERE company_id=%s'''
            cursor.execute(query, (country,id))
            connection.commit()
        elif 'workers' in request.form:
            workers=request.form['workers']
            query='''UPDATE company SET workers=%s WHERE company_id=%s'''
            cursor.execute(query, (workers,id))
            connection.commit()
        
        return redirect(url_for('company_page',id=id))
