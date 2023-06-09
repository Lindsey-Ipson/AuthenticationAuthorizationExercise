from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    
    feedback = db.relationship('Feedback', backref='user', cascade='all,delete')

    def __repr__(self):
        return f'User id={self.id} username={self.username} password={self.password} email={self.email} first_name={self.first_name} last_name={self.last_name}'
    
    @classmethod
    def register(cls, username, pwd, first_name, last_name, email):

        hashed = bcrypt.generate_password_hash(pwd)
        hashed_utf8 = hashed.decode('utf8')

        new_user = cls(
            username=username,
            password=hashed_utf8,
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        db.session.add(new_user)
        return new_user
    
    @classmethod
    def authenticate(cls, username, pwd):

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False


class Feedback(db.Model):

    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username'), nullable=False)

    def __repr__(self):
        return f'Feedback id={self.id} title={self.title} content={self.content} user={self.user}'
    

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)
    return app






# class Feedback(db.Model):

#     __tablename__ = 'feedback'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     title = db.Column(db.String(100), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     username = db.relationship('User', backref='feedback')


# class Feedback(db.Model):
#     """Feedback."""

#     __tablename__ = "feedback"

#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     username = db.Column(
#         db.String(20),
#         db.ForeignKey('users.username'),
#         nullable=False,
#     )
