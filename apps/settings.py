"""
settings.py

Configuration for Flask app

"""

from datetime import timedelta

class Config:
    # Set secret key to use session
    SECRET_KEY = "je22.zlciei1234j.,mcxv13390lk;jafmwerkqwj;adkfj;asdlfweqmklasdfjka;lfmqeiwkr;qwejir;324;kelvmkcmv;difq"
    debug = False
#    PERMANENT_SESSION_LIFETIME = timedelta(minutes=25)


class Production(Config):
    debug = True
    CSRF_ENABLED = False
    ADMIN = "jeinsong200@gmail.com"

    SQLALCHEMY_DATABASE_URI = 'mysql://root:111111@localhost/study'
    
    migration_directory = 'migrations'
    UPLOAD_FOLDER = './uploads/'
 

