

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Mateo0106(@localhost/mechanic'
    DEBUG = True
    
class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'

class ProductionConfig:
    pass
    