class Config:
    SECRET_KEY = '12928219AAB7172'

class DevelopmentConfig(Config):
    #DEBUG=True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'aab@217rab'
    MYSQL_DB = 'noteworld'

config={
    'development':DevelopmentConfig
}


#NO TE OLVIDES, CONTRA SE LINUX: 1234 