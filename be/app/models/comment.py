from datetime import datetime

from app import db


class Comment(db.Model):
    """
    Comment model representing comments on posts.
    
    Comments belong to a post and are authored by a user.
    """
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """
        Convert comment object to dictionary representation.
        
        Returns:
            dict: Comment data
        """
        return {
            'id': self.id,
            'post_id': self.post_id,
            'author_id': self.author_id,
            'author': self.author.username if self.author else None,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
