from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from FantasyFootball.Model import Base
from FantasyFootball.Model.schema import Team, Player, User


engine = create_engine('sqlite:///fantasyfootball.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

firstUser = User (name='Aamir Khan',
    email='aamir.majeed@gmail.com',provider='facebook')
session.add(firstUser)
session.commit()

chelsea = Team(name="Chelsea",
                description="Chelsea Football Club are a" +
                " professional football club based in "+
                "Fulham, London, who play in the Premier "+
                "League, the highest level of English football.",
                user_id=firstUser.id )
session.add(chelsea)
session.commit()

player1 = Player(name='Dieago Costa', position='Striker',
                    team=chelsea,
                    user_id=firstUser.id )
session.add(player1)
session.commit()
player2 = Player(name='Eden Hazard', position='Mid-Fielder',
                    team=chelsea,
                    user_id=firstUser.id )
session.add(player2)
session.commit()
player3 = Player(name='Pedro', position='Striker',
                    team=chelsea,
                    user_id=firstUser.id )
session.add(player3)
session.commit()
player4 = Player(name='Asmir Begovic', position='GoalKeeper',
                    team=chelsea,
                    user_id=firstUser.id )
session.add(player4)
session.commit()
player5 = Player(name='John Terry', position='Defender',
                    team=chelsea,
                    user_id=firstUser.id )
session.add(player5)
session.commit()
#Liverpool Team
liverpool = Team(name = 'Liverpool',
                    description = 'Liverpool Football Club are a '\
                    'Premier League football club based in Liverpool, '\
                    'England. The club have won more European trophies '\
                    'than any other English team with five European Cups,'\
                    'three UEFA Cups and three UEFA Super Cups.',
                    user_id=firstUser.id )
session.add(liverpool)
session.commit()
#Barcelona Team
barcelona = Team(name = 'Barcelona',
                    description = 'Futbol Club Barcelona, also known'\
                    'as Barcelona and familiarly as Barca, is a '\
                    'professional football club, based in Barcelona, '\
                    'Catalonia, Spain',
                    user_id=firstUser.id ) 
session.add(barcelona)
session.commit()
#ReadMadrid Team
realmadrid = Team(name = 'RealMadrid',
                    description = 'Real Madrid Club Futbol, commonly '\
                    'known as Real Madrid, or simply as Real, is a '\
                    'professional football club based in Madrid, Spain.'\
                    'Founded in 1902 as Madrid Football Club, the team '\
                    'has traditionally worn a white home kit since '\
                    'inception',
                    user_id=firstUser.id ) 
session.add(realmadrid)
session.commit()

#Machester United
manunited = Team(name = 'ManUnited',
                    description = 'Manchester United Football Club is a '\
                    'professional football club based in Old Trafford, '\
                    'Greater Manchester, England. They compete in the '\
                    'Premier League, the top flight of English football.',
                    user_id=firstUser.id )
session.add(manunited)
session.commit()