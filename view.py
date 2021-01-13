from flask.helpers import flash, url_for

from user import User, Comment
from flask import render_template, current_app, abort, redirect
from flask.globals import request
from flask_login import current_user, login_user, logout_user
from passlib.hash import pbkdf2_sha256 as hasher
from operator import itemgetter
from game import Game
import psycopg2
import os

db_url=os.environ.get("DATABASE_URL")

def insert_db():
    query='''CREATE TABLE IF NOT EXISTS company(
        company_id SERIAL PRIMARY KEY,
        company_name VARCHAR NOT NULL UNIQUE
    );'''
    cursor.execute(query)
    connection.commit()

    query='''CREATE TABLE IF NOT EXISTS genres(
        genre_id SERIAL PRIMARY KEY,
        genre_name VARCHAR NOT NULL
    );'''
    cursor.execute(query)
    connection.commit()

    query='''CREATE TABLE IF NOT EXISTS game(
        game_id SERIAL PRIMARY KEY,
        game_name VARCHAR NOT NULL,
        price NUMERIC NOT NULL,
        company_id INTEGER NOT NULL,
        age_rate INTEGER NOT NULL,
        game_mode VARCHAR(2) NOT NULL,
        trailer VARCHAR NOT NULL,
        game_info TEXT NOT NULL,
        likes INTEGER SET DEFAULT 0,
        dislikes INTEGER SET DEFAULT 0,
        FOREIGN KEY (company_id) REFERENCES company(company_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );'''
    cursor.execute(query)
    connection.commit()

    query='''CREATE TABLE IF NOT EXISTS game_genre_rel(
        genre_id INTEGER NOT NULL,
        game_id INTEGER NOT NULL,
        FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
        FOREIGN KEY (game_id) REFERENCES Game(game_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
        UNIQUE (genre_id,game_id)
    );'''
    cursor.execute(query)
    connection.commit()

    query='''CREATE TABLE IF NOT EXISTS users(
        user_id SERIAL PRIMARY KEY,
        username VARCHAR NOT NULL UNIQUE,
        name VARCHAR NOT NULL,
        birthyear INTEGER NOT NULL,
        gender VARCHAR(6),
        email VARCHAR NOT NULL UNIQUE,
        user_password VARCHAR NOT NULL,
        is_admin BOOLEAN SET DEFAULT False,
        CHECK(birthyear>=1900 and birthyear<=2021)
    );'''
    cursor.execute(query)
    connection.commit()

    query='''CREATE TABLE IF NOT EXISTS likelist(
        list_id SERIAL PRIMARY KEY,
        list_name VARCHAR,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );'''
    cursor.execute(query)
    connection.commit()

    query='''CREATE TABLE IF NOT EXISTS list_game_rel(
        list_id INTEGER NOT NULL,
        game_id INTEGER NOT NULL,
        FOREIGN KEY (list_id) REFERENCES likelist(list_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (game_id) REFERENCES Game(game_id) ON DELETE CASCADE ON UPDATE CASCADE,
        UNIQUE (list_id, game_id)
    );'''
    cursor.execute(query)
    connection.commit()

    query='''CREATE TABLE IF NOT EXISTS comments(
        comment_id SERIAL PRIMARY KEY,
        content TEXT NOT NULL,
        game_id INTEGER,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
        FOREIGN KEY (game_id) REFERENCES Game(game_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );'''
    cursor.execute(query)
    connection.commit()

    companies='''INSERT INTO company(company_name)
    VALUES ('Riot Games'),
    ('PUBG Corporation'),
    ('CD PROJEKT RED'),
    ('Innersloth'),
    ('SCS Software'),
    ('Electronic Arts'),
    ('Rockstar Games'),
    ('Crytek'),
    ('Activision'),
    ('Valve'),
    ('NetherRealm Studios'),
    ('2K'),
    ('Rocksteady Studios'),
    ('Red Barrels'),
    ('Ubisoft'),
    ('Playground Games'),
    ('Square Enix'),
    ('TaleWorlds Entertainment'),
    ('Tantalus Media'),
    ('BANDAI NAMCO Studios Inc.'),
    ('Quantic Dream'),
    ('4A Games'),
    ('SMG Studio'),
    ('Codemasters'),
    ('Motive Studios'),
    ('Berserk Games'),
    ('Mediatonic'),
    ('Mojang AB'),
    ('Blizzard Entertainment'),
    ('Infinity Ward'),
    ('CAPCOM'),
    ('Psyonix LLC');'''
    cursor.execute(companies)
    connection.commit()

    genres='''INSERT INTO genres(genre_name)
    VALUES ('MOBA'),
    ('Action'),
    ('Battle Royal'),
    ('FPS'),
    ('Sports'),
    ('Simulation'),
    ('RPG'),
    ('Casual'),
    ('Driving'),
    ('Adventure'),
    ('Puzzle'),
    ('Fighting'),
    ('Superhero'),
    ('Horror'),
    ('Racing'),
    ('Strategy'),
    ('Board Game'),
    ('Flight'),
    ('VR');'''
    cursor.execute(genres)
    connection.commit()

    games='''INSERT INTO game(game_name, price, company_id, age_rate, game_mode, trailer, game_info, likes, dislikes)
    VALUES ('League of Legends', 0, (SELECT company_id FROM company WHERE company_name='Riot Games'), 12, 'M', 'https://www.youtube.com/embed/aR-KAldshAE',
    'League of Legends is a team-based strategy game where two teams of five powerful champions face off to destroy the other’s base. Choose from over 140 champions to make epic plays, secure kills, and take down towers as you battle your way to victory.',0,0),
    ('PlayerUnknown''s Battlegrounds',87.00,(SELECT company_id FROM company WHERE company_name='PUBG Corporation'), 16, 'M', 'https://www.youtube.com/embed/YLwCfTA6LCQ', 
    'PlayerUnknown''s Battlegrounds is a battle royale shooter that pits 100 players against each other in a struggle for survival. Gather supplies and outwit your opponents to become the last person standing.', 0,0),
    ('FIFA 21',419.99,(SELECT company_id FROM company WHERE company_name='Electronic Arts'), 3, 'MS', 'https://www.youtube.com/embed/tuLAn9adQpI', 
    'FIFA 21 is a football simulation video game with lots of modes like "VOLTA FOOTBALL", "Ultimate Team", "Career Mode" and "House Rules".', 0,0),
    ('Cyberpunk 2077',249.00,(SELECT company_id FROM company WHERE company_name='CD PROJEKT RED'), 18, 'MS', 'https://www.youtube.com/embed/BO8lX3hDU30', 
    'Cyberpunk 2077 is an open-world, action-adventure story set in Night City, a megalopolis
    obsessed with power, glamour and body modification. You play as V, a mercenary outlaw going after a one-of-a-kind implant that is the key to immortality. You can customize your character’s cyberware, skillset and playstyle, and explore a vast city where the choices you make shape the story and the world around you.', 0,0),
    ('Among Us',10.50,(SELECT company_id FROM company WHERE company_name='Innersloth'), 7, 'M', 'https://www.youtube.com/embed/NSJ4cESNQfE', 
    'Join your crewmates in a multiplayer game of teamwork and betrayal!
    Play online or over local wifi with 4-10 players as you attempt to hold your spaceship together and return back to civilization. But beware...as there may be an alien impostor aboard!
    One crewmate has been replaced by a parasitic shapeshifter. Their goal is to eliminate the rest of the crew before the ship reaches home. The Impostor will sabotage the ship, sneak through vents, deceive, and frame others to remain anonymous and kill off the crew.
    While everyone is fixing up the ship, no one can talk to maintain anonymity. Once a body is reported, the surviving crew will openly debate who they think The Impostor is. The Impostor''s goal is to pretend that they are a member of the crew. If The Impostor is not voted off, everyone goes back to maintaining the ship until another body is found. If The Impostor is voted off, the crew wins!', 0,0),
    ('Euro Truck Simulator 2',39.00,(SELECT company_id FROM company WHERE company_name='SCS Software'), 3, 'S', 'https://www.youtube.com/embed/xlTuC18xVII', 
    'Travel across Europe as king of the road, a trucker who delivers important cargo across impressive distances! With dozens of cities to explore from the UK, Belgium, Germany, Italy, the Netherlands, Poland, and many more, your endurance, skill and speed will all be pushed to their limits. If you’ve got what it takes to be part of an elite trucking force, get behind the wheel and prove it!', 0,0),
    ('The Sims 4',279.99,(SELECT company_id FROM company WHERE company_name='Electronic Arts'), 12, 'S', 'https://www.youtube.com/embed/WjPPjU8OARg', 
    'Unleash your imagination and create a world of Sims that’s wholly unique. Explore and customize every detail, from Sims to homes and much more. Choose how Sims look, act, and dress. Determine how they’ll live out each day. Design and build incredible homes for every family, then decorate with your favorite furnishings and décor. Travel to different neighborhoods where you can meet other Sims and learn about their lives. Discover beautiful locations with distinctive environments, and go on spontaneous adventures. Manage the ups and downs of Sims’ everyday lives and see what happens when you play out realistic or fantastical scenarios. Tell your stories your way while developing relationships, pursuing careers and life aspirations, and immersing yourself in an extraordinary game where the possibilities are endless.', 0,0),
    ('Grand Theft Auto V',169.00,(SELECT company_id FROM company WHERE company_name='Rockstar Games'), 18, 'MS', 'https://www.youtube.com/embed/N-xHcvug3WI', 
    'When a young street hustler, a retired bank robber and a terrifying psychopath find themselves entangled with some of the most frightening and deranged elements of the criminal underworld, the U.S. government and the entertainment industry, they must pull off a series of dangerous heists to survive in a ruthless city in which they can trust nobody, least of all each other.', 0,0),
    ('Crysis Remastered',133.99,(SELECT company_id FROM company WHERE company_name='Crytek'), 16, 'MS', 'https://www.youtube.com/embed/u6gsOQ8HZAU', 
    'What begins as a simple rescue mission becomes the battleground of a new war as alien invaders swarm over a North Korean island chain. Armed with a powerful Nanosuit, players can become invisible to stalk enemy patrols, or boost strength to lay waste to vehicles. The Nanosuit’s speed, strength, armor, and cloaking allow creative solutions for every kind of fight, while a huge arsenal of modular weaponry provides unprecedented control over play style. In the ever-changing environment, adapt tactics and gear to dominate your enemies, in an enormous sandbox world.', 0,0),
    ('Call of Duty: Warzone',0,(SELECT company_id FROM company WHERE company_name='Activision'), 18, 'M', 'https://www.youtube.com/embed/0E44DClsX5Q', 
    'Warzone is a massive combat arena, set in the expansive and dense city of Verdansk, where up to 150 players will battle for victory, across two distinct epic modes of play, Battle Royale and Plunder.', 0,0),
    ('Red Dead Redemption 2',299.00,(SELECT company_id FROM company WHERE company_name='Rockstar Games'), 18, 'MS', 'https://www.youtube.com/embed/Dw_oH5oiUSE', 
    'America, 1899.
    Arthur Morgan and the Van der Linde gang are outlaws on the run. With federal agents and the best bounty hunters in the nation massing on their heels, the gang must rob, steal and fight their way across the rugged heartland of America in order to survive. As deepening internal divisions threaten to tear the gang apart, Arthur must make a choice between his own ideals and loyalty to the gang who raised him.
    Now featuring additional Story Mode content and a fully-featured Photo Mode, Red Dead Redemption 2 also includes free access to the shared living world of Red Dead Online, where players take on an array of roles to carve their own unique path on the frontier as they track wanted criminals as a Bounty Hunter, create a business as a Trader, unearth exotic treasures as a Collector or run an underground distillery as a Moonshiner and much more.', 0,0),
    ('Portal 2',18.50,(SELECT company_id FROM company WHERE company_name='Valve'), 12, 'S', 'https://www.youtube.com/embed/tax4e4hBBZc', 
    'The single-player portion of Portal 2 introduces a cast of dynamic new characters, a host of fresh puzzle elements, and a much larger set of devious test chambers. Players will explore never-before-seen areas of the Aperture Science Labs and be reunited with GLaDOS, the occasionally murderous computer companion who guided them through the original game.
    The game’s two-player cooperative mode features its own entirely separate campaign with a unique story, test chambers, and two new player characters. This new mode forces players to reconsider everything they thought they knew about portals. Success will require them to not just act cooperatively, but to think cooperatively.', 0,0),
    ('Mortal Kombat 11',82.00,(SELECT company_id FROM company WHERE company_name='NetherRealm Studios'), 18, 'MS', 'https://www.youtube.com/embed/7zwQPJmg-Kg', 
    'MK is back and better than ever in the next evolution of the iconic franchise.
    The all new Custom Character Variations give you unprecedented control of your fighters to make them your own. The new graphics engine showcases every skull-shattering, eye-popping moment, bringing you so close to the fight you can feel it. Featuring a roster of new and returning Klassic Fighters, Mortal Kombat''s best-in-class cinematic story mode continues the epic saga over 25 years in the making.', 0,0),
    ('NBA 2K21',419.00,(SELECT company_id FROM company WHERE company_name='2K'), 3, 'MS', 'https://www.youtube.com/embed/Jy00FgZNias', 
    'With extensive improvements upon its best-in-class graphics and gameplay, competitive and community online features, and deep, varied game modes, NBA 2K21 offers one-of-a-kind immersion into all facets of NBA basketball and culture - where Everything is Game.', 0,0),
    ('Injustice: Gods Among Us Ultimate Edition',31.00,(SELECT company_id FROM company WHERE company_name='NetherRealm Studios'), 16, 'MS', 'https://www.youtube.com/embed/hMkTQSbE6Bc', 
    'Injustice: Gods Among Us Ultimate Edition enhances the bold new franchise to the fighting game genre from NetherRealm Studios. Featuring six new playable characters, over 30 new skins, and 60 new S.T.A.R. Labs missions, this edition packs a punch. In addition to DC Comics icons such as Batman, The Joker, Green Lantern, The Flash, Superman and Wonder Woman, the latest title from the award-winning studio presents a deep original story. Heroes and villains will engage in epic battles on a massive scale in a world where the line between good and evil has been blurred.', 0,0),
    ('Counter-Strike: Global Offensive',0,(SELECT company_id FROM company WHERE company_name='Valve'), 18, 'M', 'https://www.youtube.com/embed/edYCtaNueQY', 
    'Counter-Strike: Global Offensive (CS: GO) expands upon the team-based action gameplay that it pioneered when it was launched 19 years ago.
    CS: GO features new maps, characters, weapons, and game modes, and delivers updated versions of the classic CS content (de_dust2, etc.).', 0,0),
    ('The Witcher 3: Wild Hunt',59.99,(SELECT company_id FROM company WHERE company_name='CD PROJEKT RED'), 18, 'S', 'https://www.youtube.com/embed/1-l29HlKkXU', 
    'The Witcher: Wild Hunt is a story-driven open world RPG set in a visually stunning fantasy universe full of meaningful choices and impactful consequences. In The Witcher, you play as professional monster hunter Geralt of Rivia tasked with finding a child of prophecy in a vast open world rich with merchant cities, pirate islands, dangerous mountain passes, and forgotten caverns to explore.', 0,0),
    ('STAR WARS Battlefront™ II',279.99,(SELECT company_id FROM company WHERE company_name='Electronic Arts'), 16, 'MS', 'https://www.youtube.com/embed/_q51LZ2HpbE', 
    'Be the hero in the ultimate Star Wars™ battle fantasy. Put your mastery of the blaster, lightsaber, and the Force to the test in massive online battles, offline scuffles against AI bots, or together in Co-Op. See what’s new in our latest Community Update.
    Play as—and against—Star Wars most feared villains and cherished heroes from all three eras, including Kylo Ren, Rey, Darth Maul, Yoda, and many more. Unique, upgradable abilities ensure classic characters bring their distinct powers and personality to the battle.', 0,0),
    ('Batman: Arkham Asylum',31.00,(SELECT company_id FROM company WHERE company_name='Rocksteady Studios'), 16, 'S', 'https://www.youtube.com/embed/T8bu2Y_cZb8', 
    'Based on the core Batman license, experience a unique, dark and atmospheric adventure that will take you to the depths of Arkham Asylum. Move in the shadows, instigate fear amongst your enemies and confront the Joker and Gotham City’s most notorious villains who have taken over the asylum. Use a wide range of Batman gadgets and abilities as you become the invisible predator and attempt to foil the Joker’s demented scheme.', 0,0),
    ('Batman: Arkham City',31.00,(SELECT company_id FROM company WHERE company_name='Rocksteady Studios'), 16, 'S', 'https://www.youtube.com/embed/jRKpUpyPCCg', 
    'Batman: Arkham City builds on the intense, atmospheric foundation of Batman: Arkham Asylum, sending players soaring into Arkham City, the new maximum security "home" for all of Gotham City''s thugs, gangsters and insane criminal masterminds. Set inside the heavily fortified walls of a sprawling district in the heart of Gotham City, this highly anticipated sequel introduces a brand-new story that draws together a new all-star cast of classic characters and murderous villains from the Batman universe, as well as a vast range of new and enhanced gameplay features to deliver the ultimate experience as the Dark Knight.', 0,0),
    ('Batman: Arkham Knight',59.00,(SELECT company_id FROM company WHERE company_name='Rocksteady Studios'), 18, 'S', 'https://www.youtube.com/embed/wsf78BS9VE0', 
    'In the explosive finale to the Arkham series, Batman faces the ultimate threat against the city he is sworn to protect. The Scarecrow returns to unite an impressive roster of super villains, including Penguin, Two-Face and Harley Quinn, to destroy The Dark Knight forever. Batman: Arkham Knight introduces Rocksteady''s uniquely designed version of the Batmobile, which is drivable for the first time in the franchise. The addition of this legendary vehicle, combined with the acclaimed gameplay of the Batman Arkham series, offers gamers the ultimate and complete Batman experience as they tear through the streets and soar across the skyline of the entirety of Gotham City.', 0,0),
    ('Outlast',32.00,(SELECT company_id FROM company WHERE company_name='Red Barrels'), 18, 'S', 'https://www.youtube.com/embed/uKA-IA4locM', 
    'Hell is an experiment you can''t survive in Outlast, a first-person survival horror game developed by veterans of some of the biggest game franchises in history. As investigative journalist Miles Upshur, explore Mount Massive Asylum and try to survive long enough to discover its terrible secret... if you dare.', 0,0),
    ('Assassin''s Creed Valhalla',269.00,(SELECT company_id FROM company WHERE company_name='Ubisoft'), 18, 'S', 'https://www.youtube.com/embed/L0Fr3cS3MtY', 
    'Become Eivor, a Viking raider raised to be a fearless warrior, and lead your clan from icy desolation in Norway to a new home amid the lush farmlands of ninth-century England. Find your settlement and conquer this hostile land by any means to earn a place in Valhalla.
    England in the age of the Vikings is a fractured nation of petty lords and warring kingdoms. Beneath the chaos lies a rich and untamed land waiting for a new conqueror. Will it be you?', 0,0),
    ('Forza Horizon 4',260.00,(SELECT company_id FROM company WHERE company_name='Playground Games'), 3, 'MS', 'https://www.youtube.com/embed/5xy4n73WOMM', 
    'For the first time in the racing and driving genre, experience dynamic seasons in a shared open-world. Explore beautiful scenery, collect over 450 cars, and become a Horizon Superstar in historic Britain.', 0,0),
    ('Dota 2',0,(SELECT company_id FROM company WHERE company_name='Valve'), 12, 'M', 'https://www.youtube.com/embed/-cSFPIwMEq4', 
    'Every day, millions of players worldwide enter battle as one of over a hundred Dota heroes. And no matter if it''s their 10th hour of play or 1,000th, there''s always something new to discover. With regular updates that ensure a constant evolution of gameplay, features, and heroes, Dota 2 has taken on a life of its own.', 0,0),
    ('Battlefield 1',279.99,(SELECT company_id FROM company WHERE company_name='Electronic Arts'), 18, 'MS', 'https://www.youtube.com/embed/NGILnNjjMZk', 
    'Battlefield™ 1 takes you back to The Great War, WW1, where new technology and worldwide conflict changed the face of warfare forever. Take part in every battle, control every massive vehicle, and execute every maneuver that turns an entire fight around. The whole world is at war – see what’s beyond the trenches.', 0,0),
    ('Marvel''s Avengers',289.00,(SELECT company_id FROM company WHERE company_name='Square Enix'), 3, 'MS', 'https://www.youtube.com/embed/LDBojdBAjXU', 
    'Assemble your team of Earth’s Mightiest Heroes, embrace your powers, and live your Super Hero dreams.
    Marvel’s Avengers is an epic, third-person, action-adventure game that combines an original, cinematic story with single-player and co-operative gameplay*. Assemble into a team of up to four players online, master extraordinary abilities, customize a growing roster of Heroes, and defend the Earth from escalating threats.', 0,0),
    ('Mount & Blade II: Bannerlord',149.99,(SELECT company_id FROM company WHERE company_name='TaleWorlds Entertainment'), 18, 'MS', 'https://www.youtube.com/embed/t4rC1awiovs', 
    'Mount & Blade II: Bannerlord is the eagerly awaited sequel to the acclaimed medieval combat simulator and role-playing game Mount & Blade: Warband. Set 200 years before, it expands both the detailed fighting system and the world of Calradia. Bombard mountain fastnesses with siege engines, establish secret criminal empires in the back alleys of cities, or charge into the thick of chaotic battles in your quest for power.', 0,0),
    ('Valorant',0,(SELECT company_id FROM company WHERE company_name='Riot Games'), 12, 'M', 'https://www.youtube.com/embed/e_E9W2vsRbQ', 
    'VALORANT is your global competitive stage. It’s a 5v5 tac-shooter matchup to plant or defuse the Spike in a one-life-per-round, first to 13 series. More than guns and bullets, you’ll choose an Agent armed with adaptive, swift, and lethal abilities that create opportunities to let your gunplay shine.
    Creativity is your greatest weapon.', 0,0),
    ('Age of Empires III',32.00,(SELECT company_id FROM company WHERE company_name='Tantalus Media'), 16, 'MS', 'https://www.youtube.com/embed/fCcRNUlE7ek', 
    'Age of Empires III completes the celebration of one of the most beloved real-time strategy franchises with remastered graphics and music, all previously released expansions and brand-new content to enjoy for the very first time.', 0,0),
    ('TEKKEN 7',119.00,(SELECT company_id FROM company WHERE company_name='BANDAI NAMCO Studios Inc.'), 16, 'MS', 'https://www.youtube.com/embed/kKLCwDg2JLA', 
    'Discover the epic conclusion of the Mishima clan and unravel the reasons behind each step of their ceaseless fight. Powered by Unreal Engine 4, TEKKEN 7 features stunning story-driven cinematic battles and intense duels that can be enjoyed with friends and rivals alike through innovative fight mechanics.
    Love, Revenge, Pride. Everyone has a reason to fight. Values are what define us and make us human, regardless of our strengths and weaknesses. There are no wrong motivations, just the path we choose to take.', 0,0),
    ('Left 4 Dead 2',18.50,(SELECT company_id FROM company WHERE company_name='Valve'), 18, 'MS', 'https://www.youtube.com/embed/wJMF-zxgbLc', 
    'Set in the zombie apocalypse, Left 4 Dead 2 (L4D2) is the highly anticipated sequel to the award-winning Left 4 Dead, the #1 co-op game of 2008.
    This co-operative action horror FPS takes you and your friends through the cities, swamps and cemeteries of the Deep South, from Savannah to New Orleans across five expansive campaigns.
    You''ll play as one of four new survivors armed with a wide and devastating array of classic and upgraded weapons. In addition to firearms, you''ll also get a chance to take out some aggression on infected with a variety of carnage-creating melee weapons, from chainsaws to axes and even the deadly frying pan.', 0,0),
    ('Detroit: Become Human',142.00,(SELECT company_id FROM company WHERE company_name='Quantic Dream'), 18, 'S', 'https://www.youtube.com/embed/jzw8rqI4dxU', 
    'Detroit 2038. Technology has evolved to a point where human like androids are everywhere. They speak, move and behave like human beings, but they are only machines serving humans.
    Play three distinct androids and see a world at the brink of chaos – perhaps our future - through their eyes. Your very decisions will dramatically alter how the game’s intense, branching narrative plays out.
    You will face moral dilemmas and decide who lives or dies. With thousands of choices and dozens of possible endings, how will you affect the future of Detroit and humanity’s destiny?', 0,0),
    ('Far Cry 5',269.00,(SELECT company_id FROM company WHERE company_name='Ubisoft'), 18, 'MS', 'https://www.youtube.com/embed/PI-1KTy0pOA', 
    'Welcome to Hope County, Montana, land of the free and the brave but also home to a fanatical doomsday cult known as Eden’s Gate. Stand up to cult leader Joseph Seed, and his siblings, the Heralds, to spark the fires of resistance and liberate the besieged community.', 0,0),
    ('Metro Exodus',249.00,(SELECT company_id FROM company WHERE company_name='4A Games'), 18, 'S', 'https://www.youtube.com/embed/fbbqlvuovQ0', 
    'The year is 2036.
    A quarter-century after nuclear war devastated the earth, a few thousand survivors still cling to existence beneath the ruins of Moscow, in the tunnels of the Metro.
    They have struggled against the poisoned elements, fought mutated beasts and paranormal horrors, and suffered the flames of civil war.
    But now, as Artyom, you must flee the Metro and lead a band of Spartan Rangers on an incredible, continent-spanning journey across post-apocalyptic Russia in search of a new life in the East.
    Metro Exodus is an epic, story-driven first person shooter from 4A Games that blends deadly combat and stealth with exploration and survival horror in one of the most immersive game worlds ever created.
    Explore the Russian wilderness across vast, non-linear levels and follow a thrilling story-line that spans an entire year through spring, summer and autumn to the depths of nuclear winter.
    Inspired by the novels of Dmitry Glukhovsky, Metro Exodus continues Artyom’s story in the greatest Metro adventure yet.', 0,0),
    ('RISK: Global Domination',0,(SELECT company_id FROM company WHERE company_name='SMG Studio'), 7, 'M', 'https://www.youtube.com/embed/srUAYq1Pxt4', 
    'Everybody wants to rule the world! Now you can play the classic game of Hasbro''s RISK online.', 0,0),
    ('F1 2020',92.00,(SELECT company_id FROM company WHERE company_name='Codemasters'), 3, 'MS', 'https://www.youtube.com/embed/T58oOjZW-BE', 
    'F1® 2020 is the most comprehensive F1® game yet, putting players firmly in the driving seat as they race against the best drivers in the world. For the first time, players can create their own F1® team by creating a driver, then choosing a sponsor, an engine supplier, hiring a teammate and competing as the 11th team on the grid. Build facilities, develop the team over time and drive to the top.', 0,0),
    ('STAR WARS: Squadrons',279.99,(SELECT company_id FROM company WHERE company_name='Motive Studios'), 12, 'MS', 'https://www.youtube.com/embed/nCcfJ9uEwvs', 
    'Master the art of starfighter combat in the authentic piloting experience STAR WARS™: Squadrons. Buckle up and feel the adrenaline of first-person, multiplayer space dogfights alongside your squadron. Pilots who enlist will step into the cockpits of starfighters from both the New Republic and Imperial fleets and fight in strategic 5v5 space battles. Modify your starfighter, and adjust the composition of your squadron to suit varying playstyles and crush the opposition. Pilots will triumph as a team and complete tactical objectives across known and never-before-seen battlefields, including the gas giant of Yavin Prime and the shattered moon of Galitan. Take control of starfighters such as the X-wing and TIE fighter. Customize loadouts and cosmetics. Divert power between weapons, shields, and engines while immersing yourself in the cockpit. In addition, players will have the option to play the entirety of the game in virtual reality (VR)!', 0,0),
    ('Tabletop Simulator',31.00,(SELECT company_id FROM company WHERE company_name='Berserk Games'), 7, 'M', 'https://www.youtube.com/embed/JBqernEHjUc', 
    'Create your own original games, import custom assets, automate games with scripting, set up complete RPG dungeons, manipulate the physics, create hinges & joints, and of course flip the table when you are losing the game. All with an easy to use system integrated with Steam Workshop. You can do anything you want in Tabletop Simulator. The possibilities are endless!
    Tabletop Simulator has it all. The base game includes 15 classics like Chess, Poker, Jigsaw Puzzles, Dominoes, and Mahjong. Additionally, there are thousands of community created content on the Workshop. If you’re the tabletop gaming type, we include an RPG Kit which has tilesets & furniture, as well as animated figurines that you can set up and battle with your friends, with even more options in the Chest. There’s even an option for Game Masters so they can control the table!', 0,0),
    ('Fall Guys: Ultimate Knockout',38.00,(SELECT company_id FROM company WHERE company_name='Mediatonic'), 3, 'M', 'https://www.youtube.com/embed/Wj3dUvGLjNQ', 
    'Fall Guys: Ultimate Knockout flings hordes of contestants together online in a mad dash through round after round of escalating chaos until one victor remains! Battle bizarre obstacles, shove through unruly competitors, and overcome the unbending laws of physics as you stumble towards greatness. Leave your dignity at the door and prepare for hilarious failure in your quest to claim the crown!', 0,0),
    ('Assassin''s Creed Odyssey',269.00,(SELECT company_id FROM company WHERE company_name='Ubisoft'), 18, 'S', 'https://www.youtube.com/embed/s_SJZSAtLBA', 
    'Write your own epic odyssey and become a legendary Spartan hero. Forge your destiny in a world on the brink of tearing itself apart. Influence how history unfolds in an ever-changing world shaped by your choices.', 0,0),
    ('Assassin''s Creed Syndicate',179.00,(SELECT company_id FROM company WHERE company_name='Ubisoft'), 18, 'S', 'https://www.youtube.com/embed/WTBbwgsyxvg', 
    '1868 London. The Industrial Revolution. An age of invention and wealth, built on the backs of the working class. As gangster killer Jacob Frye, you recruit a gang to fight for justice on behalf of the oppressed working class. Lead the underworld to reclaim London in an adventure filled with action, intrigue and brutal combat. With Jacob as the leader, players can establish UK''s fiercest gang, the only force that can challenge the elite and defeat rival gangs to bring freedom to the oppressed folks. Enemy strongholds can be infiltrated by using an arsenal to dominate London''s underworld. From robbing trains to rescuing child workers, players will do everything they can to bring justice to London’s lawless streets.', 0,0),
    ('Shadow of the Tomb Raider',209.00,(SELECT company_id FROM company WHERE company_name='Square Enix'), 18, 'S', 'https://www.youtube.com/embed/r_WbvIDAcA4', 
    'Experience Lara Croft''s defining moment as she becomes the Tomb Raider. In Shadow of the Tomb Raider, Lara must master a deadly jungle, overcome terrifying tombs, and persevere through her darkest hour. As she races to save the world from a Maya apocalypse, Lara will ultimately be forged into the Tomb Raider she is destined to be.', 0,0),
    ('Grand Theft Auto: San Andreas',18.00,(SELECT company_id FROM company WHERE company_name='Rockstar Games'), 18, 'S', 'https://www.youtube.com/embed/2NNSNTYR12M', 
    'Five years ago Carl Johnson escaped from the pressures of life in Los Santos, San Andreas... a city tearing itself apart with gang trouble, drugs and corruption. Where filmstars and millionaires do their best to avoid the dealers and gangbangers. Now, it''s the early 90s. Carl''s got to go home. His mother has been murdered, his family has fallen apart and his childhood friends are all heading towards disaster. On his return to the neighborhood, a couple of corrupt cops frame him for homicide. CJ is forced on a journey that takes him across the entire state of San Andreas, to save his family and to take control of the streets.', 0,0),
    ('Grand Theft Auto: Vice City',419.99,(SELECT company_id FROM company WHERE company_name='Rockstar Games'), 18, 'S', 'https://www.youtube.com/embed/f_VBXRZuHTc', 
    'Welcome to Vice City. Welcome to the 1980s. Having just made it back onto the streets of Liberty City after a long stretch in maximum security, Tommy Vercetti is sent to Vice City by his old boss, Sonny Forelli. They were understandably nervous about his re-appearance in Liberty City, so a trip down south seemed like a good idea. But all does not go smoothly upon his arrival in the glamorous, hedonistic metropolis of Vice City. He''s set up and is left with no money and no merchandise. Sonny wants his money back, but the biker gangs, Cuban gangsters, and corrupt politicians stand in his way. Most of Vice City seems to want Tommy dead. His only answer is to fight back and take over the city himself. Vice City offers vehicular pleasures to suit every taste. For the speed enthusiast, there''s high-performance cars and motorbikes. For the sportsman, a powerboat or a golf buggy lets you enjoy the great outdoors. For those that need that sense of freedom and escape, why not charter a helicopter and see the beauty of Vice City from the air?', 0,0),
    ('Minecraft',86.00,(SELECT company_id FROM company WHERE company_name='Mojang AB'), 3, 'MS', 'https://www.youtube.com/embed/MmB9b5njVbA', 
    'The game involves players creating and destroying various types of blocks in a three dimensional environment. The player takes an avatar that can destroy or create blocks, forming fantastic structures, creations and artwork across the various multiplayer servers in multiple game modes.', 0,0),
    ('Overwatch',125.00,(SELECT company_id FROM company WHERE company_name='Blizzard Entertainment'), 12, 'M', 'https://www.youtube.com/embed/dushZybUYnM', 
    'Overwatch is a highly stylized team-based shooter set on earth in the near future. Every match is an intense multiplayer showdown pitting a diverse cast of soldiers, mercenaries, scientists, adventurers, and oddities against each other in an epic, globe-spanning conflict.', 0,0),
    ('Call of Duty: Modern Warfare',49.00,(SELECT company_id FROM company WHERE company_name='Infinity Ward'), 18, 'MS', 'https://www.youtube.com/embed/bH1lHCirCGI', 
    'As Call of Duty 4: Modern Warfare''s single player campaign unfolds, the player is introduced to new gameplay at every turn – one moment you are fast-roping from your Black Hawk helicopter after storming into the war zone with an armada of choppers, the next you are a sniper, under concealment, in a Ghillie suit miles behind enemy lines, the next you are engaging hostiles from an AC-130 gunship thousands of feet above the battlefield.', 0,0),
    ('Call of Duty: Modern Warfare 2',49.00,(SELECT company_id FROM company WHERE company_name='Infinity Ward'), 18, 'MS', 'https://www.youtube.com/embed/TiFSSpYdPuc', 
    'Modern Warfare 2 continues the gripping and heart-racing action as players face off against a new threat dedicated to bringing the world to the brink of collapse. An entirely new gameplay mode which supports 2-player co-operative play online that is unique from the single player story campaign. Special Ops pits players into a gauntlet of time-trial and objective-based missions. Rank-up as players unlock new Special Ops missions, each more difficult. Missions include highlights from the single player campaign, fan favorites from Call of Duty 4: Modern Warfare and all new, exclusive missions.', 0,0),
    ('Call of Duty: Modern Warfare 3',99.00,(SELECT company_id FROM company WHERE company_name='Infinity Ward'), 18, 'MS', 'https://www.youtube.com/embed/coiTJbr9m04', 
    'Call of Duty: Modern Warfare 3 is a direct sequel to the previous game in the series, Call of Duty: Modern Warfare 2, with a campaign storyline continuing the struggle of U.S. forces against an invasion by the Russian Federation following the framing of an undercover U.S. agent in a terrorist attack on Moscow. Together with classic Call of Duty multi-character control, Modern Warfare 3 contains deep multiplayer support, including two-player Co-op Survival mode. The game also contains all-new Kill Streak categories and customizable strike packages that offer more options for player combat styles and strategies.', 0,0),
    ('Hearthstone',0,(SELECT company_id FROM company WHERE company_name='Blizzard Entertainment'), 7, 'MS', 'https://www.youtube.com/embed/o84Y_cSjVyE', 
    'Hearthstone is a free-to-play digital strategy card game that anyone can enjoy. Players choose one of nine epic Warcraft heroes to play as, and then take turns playing cards from their customizable decks to cast potent spells, use heroic weapons or abilities, or summon powerful characters to crush their opponent.', 0,0),
    ('Resident Evil 3',259.00,(SELECT company_id FROM company WHERE company_name='CAPCOM'), 18, 'MS', 'https://www.youtube.com/embed/xNjGFUaorYc', 
    'Fight your way to freedom from the brink of despair. A series of strange disappearances have been occurring in the American Midwest within a place called Racoon City. A specialist squad of the police force known as S.T.A.R.S. has been investigating the case, and have determined that the pharmaceutical company Umbrella and their biological weapon, the T-Virus, are behind the incidentsthough they''ve lost several members in the process. Jill Valentine and the other surviving S.T.A.R.S. members try to make this truth known, but find that the police department itself is under Umbrella''s sway and their reports are rejected out of hand.
    However, soon reports of a grisly "cannibal virus" begin to surface, and vicious dogs begin roaming the streets. With the viral plague spreading through the town and to her very doorstep, Jill is determined to survive.
    However, unbeknownst to Jill, an extremely powerful pursuer has already been dispatched to eliminate her.', 0,0),
    ('Injustice 2',77.00,(SELECT company_id FROM company WHERE company_name='NetherRealm Studios'), 16, 'MS', 'https://www.youtube.com/embed/oDav-JfidL0', 
    'Every battle defines you.Power up and build the ultimate version of your favorite DC legends in INJUSTICE 2. With a massive selection of DC Super Heroes and Super-Villains, INJUSTICE 2 allows you to equip every iconic character with unique and powerful gear earned throughout the game. Experience an unprecedented level of control over how your favorite characters look, how they fight, and how they develop across a huge variety of game modes. This is your super Hero. Your Journey. Your Injustice.', 0,0),
    ('Rocket League',0,(SELECT company_id FROM company WHERE company_name='Psyonix LLC'), 3, 'M', 'https://www.youtube.com/embed/OmMF9EDbmQQ', 
    'Soccer meets driving once again in this physics-based multiplayer-focused sequel to Supersonic Acrobatic Rocket-Powered Battle-Cars. Choose a variety of high-flying vehicles equipped with huge rocket boosters to score aerial goals and pull-off game-changing saves.', 0,0);
    '''
    cursor.execute(games)
    connection.commit()

    gamegenres='''INSERT INTO game_genre_rel(game_id, genre_id)
    VALUES ((SELECT game_id FROM game WHERE game_name='League of Legends'), (SELECT genre_id FROM genres WHERE genre_name='MOBA')),
    ((SELECT game_id FROM game WHERE game_name='PlayerUnknown''s Battlegrounds'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='PlayerUnknown''s Battlegrounds'), (SELECT genre_id FROM genres WHERE genre_name='Battle Royal')),
    ((SELECT game_id FROM game WHERE game_name='PlayerUnknown''s Battlegrounds'), (SELECT genre_id FROM genres WHERE genre_name='FPS')),
    ((SELECT game_id FROM game WHERE game_name='FIFA 21'), (SELECT genre_id FROM genres WHERE genre_name='Sports')),
    ((SELECT game_id FROM game WHERE game_name='FIFA 21'), (SELECT genre_id FROM genres WHERE genre_name='Simulation')),
    ((SELECT game_id FROM game WHERE game_name='Cyberpunk 2077'), (SELECT genre_id FROM genres WHERE genre_name='RPG')),
    ((SELECT game_id FROM game WHERE game_name='Among Us'), (SELECT genre_id FROM genres WHERE genre_name='Casual')),
    ((SELECT game_id FROM game WHERE game_name='Among Us'), (SELECT genre_id FROM genres WHERE genre_name='Battle Royal')),
    ((SELECT game_id FROM game WHERE game_name='Euro Truck Simulator 2'), (SELECT genre_id FROM genres WHERE genre_name='Driving')),
    ((SELECT game_id FROM game WHERE game_name='Euro Truck Simulator 2'), (SELECT genre_id FROM genres WHERE genre_name='Simulation')),
    ((SELECT game_id FROM game WHERE game_name='The Sims 4'), (SELECT genre_id FROM genres WHERE genre_name='Simulation')),
    ((SELECT game_id FROM game WHERE game_name='The Sims 4'), (SELECT genre_id FROM genres WHERE genre_name='RPG')),
    ((SELECT game_id FROM game WHERE game_name='Grand Theft Auto V'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Grand Theft Auto V'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Crysis Remastered'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Crysis Remastered'), (SELECT genre_id FROM genres WHERE genre_name='FPS')),
    ((SELECT game_id FROM game WHERE game_name='Call of Duty: Warzone'), (SELECT genre_id FROM genres WHERE genre_name='FPS')),
    ((SELECT game_id FROM game WHERE game_name='Call of Duty: Warzone'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Call of Duty: Warzone'), (SELECT genre_id FROM genres WHERE genre_name='Battle Royal')),
    ((SELECT game_id FROM game WHERE game_name='Red Dead Redemption 2'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Red Dead Redemption 2'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Portal 2'), (SELECT genre_id FROM genres WHERE genre_name='Puzzle')),
    ((SELECT game_id FROM game WHERE game_name='Mortal Kombat 11'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Mortal Kombat 11'), (SELECT genre_id FROM genres WHERE genre_name='Fighting')),
    ((SELECT game_id FROM game WHERE game_name='NBA 2K21'), (SELECT genre_id FROM genres WHERE genre_name='Simulation')),
    ((SELECT game_id FROM game WHERE game_name='NBA 2K21'), (SELECT genre_id FROM genres WHERE genre_name='Sports')),
    ((SELECT game_id FROM game WHERE game_name='Injustice: Gods Among Us Ultimate Edition'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Injustice: Gods Among Us Ultimate Edition'), (SELECT genre_id FROM genres WHERE genre_name='Fighting')),
    ((SELECT game_id FROM game WHERE game_name='Injustice: Gods Among Us Ultimate Edition'), (SELECT genre_id FROM genres WHERE genre_name='Superhero')),
    ((SELECT game_id FROM game WHERE game_name='Counter-Strike: Global Offensive'), (SELECT genre_id FROM genres WHERE genre_name='FPS')),
    ((SELECT game_id FROM game WHERE game_name='Counter-Strike: Global Offensive'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='The Witcher 3: Wild Hunt'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='The Witcher 3: Wild Hunt'), (SELECT genre_id FROM genres WHERE genre_name='RPG')),
    ((SELECT game_id FROM game WHERE game_name='The Witcher 3: Wild Hunt'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='STAR WARS Battlefront™ II'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='STAR WARS Battlefront™ II'), (SELECT genre_id FROM genres WHERE genre_name='Battle Royal')),
    ((SELECT game_id FROM game WHERE game_name='Batman: Arkham Asylum'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Batman: Arkham Asylum'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Batman: Arkham Asylum'), (SELECT genre_id FROM genres WHERE genre_name='Superhero')),
    ((SELECT game_id FROM game WHERE game_name='Batman: Arkham City'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Batman: Arkham City'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Batman: Arkham City'), (SELECT genre_id FROM genres WHERE genre_name='Superhero')),
    ((SELECT game_id FROM game WHERE game_name='Batman: Arkham Knight'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Batman: Arkham Knight'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Batman: Arkham Knight'), (SELECT genre_id FROM genres WHERE genre_name='Superhero')),
    ((SELECT game_id FROM game WHERE game_name='Outlast'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Outlast'), (SELECT genre_id FROM genres WHERE genre_name='Horror')),
    ((SELECT game_id FROM game WHERE game_name='Assassin''s Creed Valhalla'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Assassin''s Creed Valhalla'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Assassin''s Creed Valhalla'), (SELECT genre_id FROM genres WHERE genre_name='RPG')),
    ((SELECT game_id FROM game WHERE game_name='Forza Horizon 4'), (SELECT genre_id FROM genres WHERE genre_name='Racing')),
    ((SELECT game_id FROM game WHERE game_name='Forza Horizon 4'), (SELECT genre_id FROM genres WHERE genre_name='Driving')),
    ((SELECT game_id FROM game WHERE game_name='Forza Horizon 4'), (SELECT genre_id FROM genres WHERE genre_name='Simulation')),
    ((SELECT game_id FROM game WHERE game_name='Dota 2'), (SELECT genre_id FROM genres WHERE genre_name='MOBA')),
    ((SELECT game_id FROM game WHERE game_name='Battlefield 1'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Battlefield 1'), (SELECT genre_id FROM genres WHERE genre_name='FPS')),
    ((SELECT game_id FROM game WHERE game_name='Marvel''s Avengers'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Marvel''s Avengers'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Marvel''s Avengers'), (SELECT genre_id FROM genres WHERE genre_name='RPG')),
    ((SELECT game_id FROM game WHERE game_name='Marvel''s Avengers'), (SELECT genre_id FROM genres WHERE genre_name='Superhero')),
    ((SELECT game_id FROM game WHERE game_name='Mount & Blade II: Bannerlord'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Mount & Blade II: Bannerlord'), (SELECT genre_id FROM genres WHERE genre_name='Strategy')),
    ((SELECT game_id FROM game WHERE game_name='Mount & Blade II: Bannerlord'), (SELECT genre_id FROM genres WHERE genre_name='RPG')),
    ((SELECT game_id FROM game WHERE game_name='Valorant'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Valorant'), (SELECT genre_id FROM genres WHERE genre_name='FPS')),
    ((SELECT game_id FROM game WHERE game_name='Age of Empires III'), (SELECT genre_id FROM genres WHERE genre_name='Strategy')),
    ((SELECT game_id FROM game WHERE game_name='TEKKEN 7'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='TEKKEN 7'), (SELECT genre_id FROM genres WHERE genre_name='Fighting')),
    ((SELECT game_id FROM game WHERE game_name='Left 4 Dead 2'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Left 4 Dead 2'), (SELECT genre_id FROM genres WHERE genre_name='FPS')),
    ((SELECT game_id FROM game WHERE game_name='Detroit: Become Human'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Far Cry 5'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Far Cry 5'), (SELECT genre_id FROM genres WHERE genre_name='FPS')),
    ((SELECT game_id FROM game WHERE game_name='Metro Exodus'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Metro Exodus'), (SELECT genre_id FROM genres WHERE genre_name='FPS')),
    ((SELECT game_id FROM game WHERE game_name='RISK: Global Domination'), (SELECT genre_id FROM genres WHERE genre_name='Board Game')),
    ((SELECT game_id FROM game WHERE game_name='RISK: Global Domination'), (SELECT genre_id FROM genres WHERE genre_name='Strategy')),
    ((SELECT game_id FROM game WHERE game_name='F1 2020'), (SELECT genre_id FROM genres WHERE genre_name='Racing')),
    ((SELECT game_id FROM game WHERE game_name='F1 2020'), (SELECT genre_id FROM genres WHERE genre_name='Driving')),
    ((SELECT game_id FROM game WHERE game_name='F1 2020'), (SELECT genre_id FROM genres WHERE genre_name='Simulation')),
    ((SELECT game_id FROM game WHERE game_name='STAR WARS: Squadrons'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='STAR WARS: Squadrons'), (SELECT genre_id FROM genres WHERE genre_name='Flight')),
    ((SELECT game_id FROM game WHERE game_name='STAR WARS: Squadrons'), (SELECT genre_id FROM genres WHERE genre_name='VR')),
    ((SELECT game_id FROM game WHERE game_name='Tabletop Simulator'), (SELECT genre_id FROM genres WHERE genre_name='Board Game')),
    ((SELECT game_id FROM game WHERE game_name='Tabletop Simulator'), (SELECT genre_id FROM genres WHERE genre_name='Simulation')),
    ((SELECT game_id FROM game WHERE game_name='Tabletop Simulator'), (SELECT genre_id FROM genres WHERE genre_name='VR')),
    ((SELECT game_id FROM game WHERE game_name='Fall Guys: Ultimate Knockout'), (SELECT genre_id FROM genres WHERE genre_name='Casual')),
    ((SELECT game_id FROM game WHERE game_name='Fall Guys: Ultimate Knockout'), (SELECT genre_id FROM genres WHERE genre_name='Battle Royal')),
    ((SELECT game_id FROM game WHERE game_name='Assassin''s Creed Odyssey'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Assassin''s Creed Odyssey'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Assassin''s Creed Odyssey'), (SELECT genre_id FROM genres WHERE genre_name='RPG')),
    ((SELECT game_id FROM game WHERE game_name='Assassin''s Creed Syndicate'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Assassin''s Creed Syndicate'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Assassin''s Creed Syndicate'), (SELECT genre_id FROM genres WHERE genre_name='RPG')),
    ((SELECT game_id FROM game WHERE game_name='Shadow of the Tomb Raider'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Shadow of the Tomb Raider'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Grand Theft Auto: San Andreas'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Grand Theft Auto: San Andreas'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Grand Theft Auto: Vice City'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Grand Theft Auto: Vice City'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Minecraft'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Minecraft'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Overwatch'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Overwatch'), (SELECT genre_id FROM genres WHERE genre_name='FPS')),
    ((SELECT game_id FROM game WHERE game_name='Call of Duty: Modern Warfare'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Call of Duty: Modern Warfare'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Call of Duty: Modern Warfare'), (SELECT genre_id FROM genres WHERE genre_name='FPS')),
    ((SELECT game_id FROM game WHERE game_name='Call of Duty: Modern Warfare 2'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Call of Duty: Modern Warfare 2'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Call of Duty: Modern Warfare 2'), (SELECT genre_id FROM genres WHERE genre_name='FPS')),
    ((SELECT game_id FROM game WHERE game_name='Call of Duty: Modern Warfare 3'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Call of Duty: Modern Warfare 3'), (SELECT genre_id FROM genres WHERE genre_name='Adventure')),
    ((SELECT game_id FROM game WHERE game_name='Call of Duty: Modern Warfare 3'), (SELECT genre_id FROM genres WHERE genre_name='FPS')),
    ((SELECT game_id FROM game WHERE game_name='Hearthstone'), (SELECT genre_id FROM genres WHERE genre_name='Board Game')),
    ((SELECT game_id FROM game WHERE game_name='Hearthstone'), (SELECT genre_id FROM genres WHERE genre_name='Strategy')),
    ((SELECT game_id FROM game WHERE game_name='Resident Evil 3'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Resident Evil 3'), (SELECT genre_id FROM genres WHERE genre_name='Horror')),
    ((SELECT game_id FROM game WHERE game_name='Injustice 2'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
    ((SELECT game_id FROM game WHERE game_name='Injustice 2'), (SELECT genre_id FROM genres WHERE genre_name='Fighting')),
    ((SELECT game_id FROM game WHERE game_name='Injustice 2'), (SELECT genre_id FROM genres WHERE genre_name='Superhero')),
    ((SELECT game_id FROM game WHERE game_name='Rocket League'), (SELECT genre_id FROM genres WHERE genre_name='Racing')),
    ((SELECT game_id FROM game WHERE game_name='Rocket League'), (SELECT genre_id FROM genres WHERE genre_name='Sports'));'''
    cursor.execute(gamegenres)
    connection.commit()
    return "Yey"

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
        if 'username' in request.form and 'password' in request.form:
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
        if 'name' in request.form and 'username' in request.form and 'email' in request.form and 'year' in request.form and 'password' in request.form:
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
    genre_list=create_genrelist()
    if request.method=="GET":
        create_gamebase(db)
        games = db.get_gamelist()
    
        return render_template("pgames.html",games=games, genre_list=genre_list, title="Most Popular Games")
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
        for id in record:
            game=create_game(id[0])
            games.append((game.id,game))
        games.sort(key=itemgetter(1),reverse=True)
        return render_template("pgames.html",games=games, genre_list=genre_list, title="Games By Filter")

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
                    addlist=[x.strip() for x in request.form['genre_add'].split(',')]
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
                print(666666)
                db = current_app.config["db"]
                create_gamebase(db)
                return redirect(url_for('game_page',gameid=gameid))
            else:
                return render_template("add_game.html", genres=genres)   
        else:
            flash('Please fill in all the blanks!')
            return render_template("add_game.html", genres=genres)

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
    elif 'delete_game' in request.form:
        query='''DELETE FROM game WHERE game_id=%s'''
        cursor.execute(query,(gameid,))
        connection.commit()
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
    number='''SELECT game_id FROM game;'''
    cursor.execute(number)
    total_game_number=cursor.fetchall()
    for game_id in total_game_number:  
        db.add_game(create_game(game_id[0]))

def create_game(game_id):
    query='''SELECT * FROM game WHERE game_id=%s'''
    cursor.execute(query,(game_id,))
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
    user=User(record[0],record[1],record[2],record[3],record[4],record[5],record[6],record[7])

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
        user=User(userdata[0],userdata[1],userdata[2],userdata[3],userdata[4],userdata[5],userdata[6],userdata[7])
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

def create_genrelist():
    query='''SELECT genre_name FROM genres ORDER BY genre_name'''
    cursor.execute(query,)
    genres=[]
    for i in cursor.fetchall():
        genres.append(i[0])
    
    return genres