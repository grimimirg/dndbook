from datetime import datetime

from app import db


class CharacterMention(db.Model):
    """
    CharacterMention model representing character mentions in posts.
    
    Links characters to posts where they are mentioned via @name syntax.
    """
    __tablename__ = 'character_mentions'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    mention_text = db.Column(db.String(100), nullable=False)  # The @name text used in the post
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    post = db.relationship('Post', backref='character_mentions', lazy=True)
    character = db.relationship('Character', backref='post_mentions', lazy=True)

    def to_dict(self):
        """
        Convert character mention object to dictionary representation.
        
        Returns:
            dict: Character mention data
        """
        return {
            'id': self.id,
            'post_id': self.post_id,
            'character_id': self.character_id,
            'mention_text': self.mention_text,
            'character': self.character.to_dict() if self.character else None,
            'created_at': self.created_at.isoformat()
        }
