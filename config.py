import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    user = 'postgres'
    pwd = 'factnews'
    link = pwd + '.cnynl0ibutvj.us-west-2.rds.amazonaws.com/' + user
    SQLALCHEMY_DATABASE_URI = 'postgresql://' + user + ':' + pwd + '@' + link
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.urandom(24)  # For WTF forms
    TEMPLATES_AUTO_RELOAD = True
