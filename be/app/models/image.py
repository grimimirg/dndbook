from datetime import datetime

from app import db


class Image(db.Model):
    """
    Image model representing images attached to posts.
    
    Images are ordered within a post using the order_index field.
    """
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """
        Convert image object to dictionary representation.
        
        Returns:
            dict: Image data
        """
        return {
            'id': self.id,
            'post_id': self.post_id,
            'file_path': self.file_path,
            'order_index': self.order_index
        }
