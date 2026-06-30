from datetime import datetime

from app import db


class Note(db.Model):
    """
    Note model for freeform markdown notes.

    Notes are owned by a user and can optionally nest under a parent note.
    Visibility controls who can read the note beyond its owner.
    """
    __tablename__ = 'notes'

    VISIBILITY_PRIVATE = 'private'
    VISIBILITY_PUBLIC = 'public'
    ALLOWED_VISIBILITIES = {VISIBILITY_PRIVATE, VISIBILITY_PUBLIC}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False, default='')
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    visibility = db.Column(db.String(20), nullable=False, default=VISIBILITY_PRIVATE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=True)

    owner = db.relationship('User', backref=db.backref('notes', lazy=True, cascade='all, delete-orphan'))
    children = db.relationship('Note', backref=db.backref('parent', remote_side=[id]), lazy=True,
                               cascade='all, delete-orphan')

    def to_dict(self, include_children=False):
        """
        Convert note object to dictionary representation.

        Args:
            include_children (bool): Whether to include direct child notes in output

        Returns:
            dict: Note data
        """
        result = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'owner_id': self.owner_id,
            'owner': self.owner.username if self.owner else None,
            'visibility': self.visibility,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z',
        }
        if include_children:
            result['children'] = [child.to_dict() for child in self.children]
        return result
