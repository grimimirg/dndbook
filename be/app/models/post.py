from datetime import datetime

from app import db


class Post(db.Model):
    """
    Post model representing campaign session posts.
    
    Posts belong to a campaign and can have multiple images and comments.
    """
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    post_order = db.Column(db.Integer, nullable=True, index=True)
    importance_level = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    images = db.relationship('Image', backref='post', lazy=True, cascade='all, delete-orphan',
                             order_by='Image.order_index')
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan',
                               order_by='Comment.created_at')
    notifications = db.relationship('Notification', backref='related_post', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_images=True, include_comments=True):
        """
        Convert post object to dictionary representation.
        
        Args:
            include_images (bool): Whether to include images in output
            include_comments (bool): Whether to include comments in output
            
        Returns:
            dict: Post data with optional images and comments
        """
        result = {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'author_id': self.author_id,
            'author': self.author.username if self.author else None,
            'title': self.title,
            'content': self.content,
            'order': self.post_order,
            'importance_level': self.importance_level,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z'
        }
        if include_images:
            result['images'] = [img.to_dict() for img in self.images]
        if include_comments:
            result['comments'] = [comment.to_dict() for comment in self.comments]
        return result
