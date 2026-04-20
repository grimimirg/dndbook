from datetime import datetime

from app import db


class Campaign(db.Model):
    """
    Campaign model representing D&D campaigns.
    
    A campaign is owned by a user and can have multiple members and posts.
    """
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    posts = db.relationship('Post', backref='campaign', lazy=True, cascade='all, delete-orphan')
    characters = db.relationship('Character', backref='campaign', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_members=False):
        """
        Convert campaign object to dictionary representation.
        
        Args:
            include_members (bool): Whether to include member list in output
            
        Returns:
            dict: Campaign data with optional member information
        """
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
