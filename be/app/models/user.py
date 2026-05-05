from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models.campaign_members import CampaignMembers


class User(db.Model):
    """
    User model representing registered users in the system.
    
    Users can own campaigns, be members of campaigns, create posts, and comment.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owned_campaigns = db.relationship('Campaign', backref='owner', lazy=True, cascade='all, delete-orphan',
                                      foreign_keys='Campaign.owner_id')
    member_campaigns = db.relationship('Campaign', secondary=CampaignMembers,
                                       backref=db.backref('members', lazy='dynamic'))
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')
    sent_invites = db.relationship('CampaignInvite', foreign_keys='CampaignInvite.inviter_id', backref='inviter',
                                   lazy=True, cascade='all, delete-orphan')
    received_invites = db.relationship('CampaignInvite', foreign_keys='CampaignInvite.invitee_id', backref='invitee',
                                       lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """
        Hash and set the user's password.
        
        Args:
            password (str): Plain text password to hash
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verify a password against the stored hash.
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """
        Convert user object to dictionary representation.
        
        Returns:
            dict: User data without sensitive information
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
