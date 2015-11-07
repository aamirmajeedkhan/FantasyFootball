from sqlalchemy import create_engine
from FantasyFootball.Model import Base
from FantasyFootball.Model.schema import Team, Player


engine = create_engine('sqlite:///fantasyfootball.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.create_all(engine)