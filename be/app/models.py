from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

# Tabella di associazione per la relazione molti-a-molti tra User e Campaign
campaign_members = db.Table('campaign_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('campaign_id', db.Integer, db.ForeignKey('campaigns.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    owned_campaigns = db.relationship('Campaign', backref='owner', lazy=True, cascade='all, delete-orphan', foreign_keys='Campaign.owner_id')
    member_campaigns = db.relationship('Campaign', secondary=campaign_members, backref=db.backref('members', lazy='dynamic'))
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    sent_invites = db.relationship('CampaignInvite', foreign_keys='CampaignInvite.inviter_id', backref='inviter', lazy=True, cascade='all, delete-orphan')
    received_invites = db.relationship('CampaignInvite', foreign_keys='CampaignInvite.invitee_id', backref='invitee', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    posts = db.relationship('Post', backref='campaign', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_members=False):
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'post_count': len(self.posts)
        }
        if include_members:
            result['members'] = [{'id': m.id, 'username': m.username} for m in self.members]
            result['member_count'] = self.members.count()
        return result

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    images = db.relationship('Image', backref='post', lazy=True, cascade='all, delete-orphan', order_by='Image.order_index')
    
    def to_dict(self, include_images=True):
        result = {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'author_id': self.author_id,
            'author': self.author.username if self.author else None,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_images:
            result['images'] = [img.to_dict() for img in self.images]
        return result

class Image(db.Model):
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'file_path': self.file_path,
            'order_index': self.order_index
        }

class CampaignInvite(db.Model):
    __tablename__ = 'campaign_invites'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    inviter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
    
    campaign = db.relationship('Campaign', backref=db.backref('invites', lazy=True, cascade='all, delete-orphan'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'campaign_name': self.campaign.name if self.campaign else None,
            'inviter_id': self.inviter_id,
            'inviter_username': self.inviter.username if self.inviter else None,
            'invitee_id': self.invitee_id,
            'invitee_username': self.invitee.username if self.invitee else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'responded_at': self.responded_at.isoformat() if self.responded_at else None
        }
