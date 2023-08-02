from database.config import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # SQLAlchemy automatically makes the first int PK autoincrement
    username = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50), nullable=False)
    birthdate = db.Column(db.Date)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    online_user = db.relationship('OnlineUser', primaryjoin='User.id==OnlineUser.id')


class OnlineUser(db.Model):
    __tablename__ = 'online_users'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    username = db.Column(db.String(50))
    ipaddress = db.Column(db.String(15), nullable=False)
    login_time = db.Column(db.DateTime, nullable=False)
