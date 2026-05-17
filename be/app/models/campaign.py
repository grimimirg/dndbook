from datetime import datetime

from app import db
from app.utils.text_filter import filter_hidden_text


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
    character_creation_mode = db.Column(db.String(20), nullable=False, default='optional')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    posts = db.relationship('Post', backref='campaign', lazy=True, cascade='all, delete-orphan')
    characters = db.relationship('Character', backref='campaign', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_members=False, user=None):
        """
        Convert campaign object to dictionary representation.
        
        Args:
            include_members (bool): Whether to include member list in output
            user: The user requesting the data (used for filtering hidden text)
            
        Returns:
            dict: Campaign data with optional member information
        """
        # Filter description for non-DM users
        should_filter = user is not None and self.owner_id != user.id
        filtered_description = filter_hidden_text(self.description, should_filter)
        
        result = {
            'id': self.id,
            'name': self.name,
            'description': filtered_description,
            'owner_id': self.owner_id,
            'character_creation_mode': self.character_creation_mode,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'post_count': len(self.posts)
        }
        if include_members:
            result['members'] = [{'id': m.id, 'username': m.username} for m in self.members]
            result['member_count'] = self.members.count()
        return result
