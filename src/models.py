import datetime
import peewee
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin


DATABASE = peewee.SqliteDatabase("database/journal.db")

class User(UserMixin, peewee.Model):
    joined_at = peewee.DateTimeField(default=datetime.datetime.now)
    username = peewee.CharField(max_length=255, unique=True)
    email = peewee.CharField(unique=True)
    password = peewee.CharField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, email, password):
        try:
            cls.create(
                username=username,
                email=email,
                password=generate_password_hash(password)
            )
        except peewee.IntegrityError:
            raise ValueError("User already exist!")


class Journal(peewee.Model):
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    title = peewee.CharField(max_length=255)
    time_spent = peewee.IntegerField()
    learned = peewee.TextField()
    resourses = peewee.TextField()
    tag = peewee.CharField()
    slug = peewee.CharField()
    user = peewee.ForeignKeyField(User, backref="journals")

    class Meta:
        database = DATABASE
        order_by = ('-created_at')



def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Journal], safe=True)
    DATABASE.close()
