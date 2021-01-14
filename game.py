from operator import itemgetter

class Game:
    def __init__(self,id, name, price, company, age, mode, genre,link, content, likes=0, dislikes=0):
        self.id=id
        self.name=name
        self.company=company
        self.price=price
        self.age=age
        self.mode=mode
        self.genre=genre
        self.content=content
        self.likes=likes
        self.dislikes=dislikes
        self.link=link
        if likes== 0:
            self.score = 0
        else: 
            self.score = int((likes)  * 100 / (likes + dislikes))
    
    def __gt__(self, other):
        if self.score > other.score:
            return True
        else:
            return False
    
    def __lt__(self, other):
        if self.score < other.score:
            return True
        else:
            return False
    
    def __eq__(self, other):
        if self.score == other.score:
            return True
        else:
            return False

class Company:
    def __init__(self, id, name, ceo_name=None, year=None, country=None, workers=None):
        self.id=id
        self.name=name
        self.workers=workers
        self.ceo_name=ceo_name
        self.year=year
        self.country=country

class gamebase:
    def __init__(self):
        self.games={}
    
    def add_game(self, game):
        self.games[game.id]=game
    
    def clear_games(self):
        self.games.clear()
    
    def get_game(self, id):
        game=self.games.get(id)
        if game is None:
            return None
        else:
            retgame = Game(game.id, game.name, game.price, game.company,game.age, game.mode, game.genre,game.link, game.content, game.likes, game.dislikes)
            return retgame
    
    def get_gamelist(self):
        gamelist = []
        for id, game in self.games.items():
            gamex = Game(game.id ,game.name, game.price, game.company,game.age, game.mode, game.genre, game.link, game.content, game.likes, game.dislikes)
            gamelist.append((id,gamex))
        gamelist.sort(key=itemgetter(1),reverse=True)
        return gamelist
