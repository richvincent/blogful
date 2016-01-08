import os

psqlUser = os.environ.get('PGUSER', 'ubuntu')
psqlPassword = os.environ.get('PSPASSWORD', 'Password1')


class DevelopmentConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@localhost:\
        5432/blogful".format(psqlUser, psqlPassword)
    DEBUG = True
