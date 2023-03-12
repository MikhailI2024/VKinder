from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import DB_NAME, HOST, PASSWORD, USER

# define the database connection string
connection_string = f"postgresql://{USER}:{PASSWORD}@{HOST}/{DB_NAME}"

# create the database engine
engine = create_engine(connection_string)

# create a session factory bound to the engine
Session = sessionmaker(bind=engine)

# create a base class for declarative models
Base = declarative_base()

# define the User and SeenUser models
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(25), nullable=False)
    vk_id = Column(String(20), nullable=False, unique=True)
    vk_link = Column(String(50))

class SeenUser(Base):
    __tablename__ = 'seen_users'

    id = Column(Integer, primary_key=True)
    vk_id = Column(String(50), nullable=False, unique=True)

# create the tables
Base.metadata.create_all(engine)

def insert_data_users(first_name, last_name, vk_id, vk_link):
    """Insert data into the users table."""
    session = Session()
    user = User(first_name=first_name, last_name=last_name, vk_id=vk_id, vk_link=vk_link)
    session.add(user)
    session.commit()

def insert_data_seen_users(vk_id, shift):
    """Insert data into the seen_users table."""
    session = Session()
    user = SeenUser(vk_id=vk_id)
    session.add(user)
    session.commit()

def select(shift):
    """Select an unseen user."""
    session = Session()
    query = session.query(
        User.first_name, 
        User.last_name, 
        User.vk_id, 
        User.vk_link, 
        SeenUser.vk_id).outerjoin(
            SeenUser, User.vk_id == SeenUser.vk_id).filter(
                SeenUser.vk_id == None).offset(shift)
    return query.first()

def drop_users():
    """Drop the users table."""
    session = Session()
    session.execute(text('DROP TABLE IF EXISTS users CASCADE;'))
    session.commit()

def drop_seen_users():
    """Drop the seen_users table."""
    session = Session()
    session.execute(text('DROP TABLE IF EXISTS seen_users CASCADE;'))
    session.commit()

def creating_database():
    """Create the tables."""
    drop_users()
    drop_seen_users()
    Base.metadata.create_all(engine)

