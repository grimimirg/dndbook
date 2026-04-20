from datetime import datetime

from app import db


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """
        Convert character object to dictionary representation.
        
        Returns:
            dict: Character data
        """
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'name': self.name,
            'race': self.race,
            'character_class': self.character_class,
            'description': self.description,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
