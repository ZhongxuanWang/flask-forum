from datetime import datetime

from flask.ext.security import UserMixin, RoleMixin
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.orderinglist import ordering_list

from application import db


class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class TimestampMixin(object):

    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow)

    def readable_date(self, date, format='%H:%M on %-d %B'):
        return date.strftime(format)


# Authentication
# ~~~~~~~~~~~~~~
class UserRoleAssoc(db.Model):
    __tablename__ = 'user_role_assoc'
    user_id = db.Column(db.ForeignKey('user.id'), primary_key=True)
    role_id = db.Column(db.ForeignKey('role.id'), primary_key=True)


class User(Base, UserMixin):
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    roles = db.relationship('Role', secondary='user_role_assoc',
                            backref='users')

    def __repr__(self):
        return '<User(%s, %s)>' % (self.id, self.email)

    def __unicode__(self):
        return self.email


class Role(Base, RoleMixin):
    name = db.Column(db.String)
    description = db.Column(db.String)

    def __repr__(self):
        return '<Role(%s, %s)>' % (self.id, self.name)


# Forum
# ~~~~~
class Board(Base):
    name = db.Column(db.String)
    slug = db.Column(db.String, unique=True)
    description = db.Column(db.String)

    threads = db.relationship('Thread', cascade='all,delete')

    def __unicode__(self):
        return self.name


class Thread(Base, TimestampMixin):
    name = db.Column(db.String(80))
    author_id = db.Column(db.ForeignKey('user.id'), index=True)
    board_id = db.Column(db.ForeignKey('board.id'), index=True)

    author = db.relationship('User', backref='threads')
    posts = db.relationship('Post', backref='thread',
                            cascade='all,delete',
                            order_by='Post.index',
                            collection_class=ordering_list('index'))

    def __unicode__(self):
        return self.name

    @property
    def num_posts(self):
        return Post.query.filter(Post.thread_id == self.id).count()


class Post(Base, TimestampMixin):
    index = db.Column(db.Integer, default=0, index=True)
    content = db.Column(db.Text)
    author_id = db.Column(db.ForeignKey('user.id'), index=True)
    thread_id = db.Column(db.ForeignKey('thread.id'), index=True)

    author = db.relationship('User', backref='posts')

    def __repr__(self):
        return '<Post(%s)>' % self.id
