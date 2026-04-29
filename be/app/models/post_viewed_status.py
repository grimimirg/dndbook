from datetime import datetime

from app import db

PostViewedStatus = db.Table('post_viewed_status',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('viewed_at', db.DateTime, default=datetime.utcnow)
)
