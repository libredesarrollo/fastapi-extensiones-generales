from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+mysqlconnector://root:@localhost:3306/pruebas"
engine = create_engine(
    DATABASE_URL,
     pool_size=10,      # El cajón siempre tiene 10 llaves listas.
     max_overflow=20    # Si llegan 30 personas a la vez, fabrica 20 llaves temporales.
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_database_session():
    try:
        db = SessionLocal()
        yield db
        #return db
    finally:
        db.close()