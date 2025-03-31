
import pytest
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, DateTime, TIMESTAMP, Boolean, select, insert, delete, update

Base = declarative_base()

class Shorten_links(Base):
    __tablename__ = "shorten_links"

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    short_link = Column(String, unique=True, nullable=False)
    creation_date = Column(DateTime, nullable=False)
    last_use_date = Column(DateTime)
    expires_at = Column(DateTime)
    user_id = Column(String, nullable=True)
    

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def sample_data(db_session):
    creation_date = datetime.now()
    shortren_link = Shorten_links(
        url="https://ya.ru", 
        short_link="ya", 
        creation_date=creation_date,
        last_use_date=None, 
        expires_at=None, 
        user_id=None
    )
    db_session.add(shortren_link)
    db_session.commit()
    return shortren_link

def test_shorten_links_creation(db_session, sample_data):
    result = db_session.query(Shorten_links).first()
    
    assert result.short_link == sample_data.short_link
    assert result.url == sample_data.url
    assert result.creation_date == sample_data.creation_date
    
def test_shorten_links_update(db_session, sample_data):
    update_query = (
        update(Shorten_links)
        .where(Shorten_links.short_link == "ya")
        .values(short_link="new_ya")
    ) 
    db_session.execute(update_query)
    db_session.commit()
    
    result = db_session.query(Shorten_links).first()
    
    assert result.short_link == "new_ya"
    
def test_shorten_links_delete(db_session, sample_data):
    delete_query = delete(Shorten_links).where(Shorten_links.short_link == 'ya')
    db_session.execute(delete_query)
    db_session.commit()
    
    result = db_session.query(Shorten_links).first()
    
    assert result == None

class Users(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.now)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)
    

@pytest.fixture
def sample_data_users(db_session):
    creation_date = datetime.now()
    user = Users(
        email="user@mail.ru", 
        hashed_password="12345", 
        registered_at=creation_date,
        is_active=True, 
        is_superuser=False, 
        is_verified=False
    )
    
    db_session.add(user)
    db_session.commit()
    
    return user


def test_users_creation(db_session, sample_data_users):
    result = db_session.query(Users).first()

    assert result.email == sample_data_users.email
    assert result.hashed_password == sample_data_users.hashed_password
    assert result.registered_at == sample_data_users.registered_at



    
