from datetime import datetime

from flask import request
from app import db
from app.utils.text_filter import filter_hidden_text


class Character(db.Model):
    """
    Character model representing pre-made characters for campaigns.
    
    Characters are created by campaign owners and can be selected by players.
    """
    __tablename__ = 'characters'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    race = db.Column(db.String(50), nullable=False)
    character_class = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    is_predefined = db.Column(db.Boolean, default=False, nullable=False)
    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, user=None):
        """
        Convert character object to dictionary representation.
        
        Args:
            user: The user requesting the data (used for filtering hidden text)
        
        Returns:
            dict: Character data
        """
        # Filter description for non-DM users
        should_filter = user is not None and self.campaign.owner_id != user.id
        filtered_description = filter_hidden_text(self.description, should_filter)
        
        image_url = None
        if self.image_url:
            if self.image_url.startswith('http'):
                image_url = self.image_url
            else:
                base_url = request.host_url.rstrip('/')
                image_url = f"{base_url}{self.image_url}"
        
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'name': self.name,
            'race': self.race,
            'character_class': self.character_class,
            'description': filtered_description,
            'image_url': image_url,
            'is_predefined': self.is_predefined,
            'assigned_to_user_id': self.assigned_to_user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
