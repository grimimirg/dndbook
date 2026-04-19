from datetime import datetime

from app import db

campaign_members = db.Table('campaign_members',
                            db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                            db.Column('campaign_id', db.Integer, db.ForeignKey('campaigns.id'), primary_key=True),
                            db.Column('joined_at', db.DateTime, default=datetime.utcnow)
                            )
