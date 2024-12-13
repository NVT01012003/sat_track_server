from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.sql_model import BASE
from dotenv import load_dotenv
import os

load_dotenv()

db_user: str = os.getenv("DB_USER")
db_port: int = int(os.getenv("DB_PORT"))
db_host: str = os.getenv("DB_HOST")
db_password: str = os.getenv("DB_PASS")
db_name: str = os.getenv("DB_NAME")

uri: str = F'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

engine = create_engine(uri)

BASE.metadata.create_all(bind=engine)

#session
SessionLocal  = sessionmaker(
  autocommit=False, autoflush=False, bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

try: 
  connection = engine.connect()
  connection.close()
  print('ping, Connected')

except Exception as e: 
  print(f'Error: {str(e)}')
