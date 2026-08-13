"""Note model for personal and player-facing notes within campaigns."""

from datetime import datetime

from app import db


class Note(db.Model):
    """Note model representing DM notes within a campaign.

    Notes can be personal (DM-only) or player-visible with per-player
    permissions managed via the NotePermission cross-reference table.

    Fields:
        id: Primary key
        campaign_id: Campaign this note belongs to
        owner_id: User who created the note (always the DM/campaign owner)
        title: Note title
        content: Markdown body
        visibility: 'personal' (DM-only) or 'players' (per-player gated)
        parent_id: Optional parent note for nesting
        created_at: Creation timestamp
        updated_at: Last modification timestamp
    """
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False, default='')
    visibility = db.Column(db.String(20), nullable=False, default='personal')
    parent_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = db.relationship('User', backref='notes', foreign_keys=[owner_id])
    parent = db.relationship('Note', remote_side=[id], backref='children')
    permitted_users = db.relationship(
        'User',
        secondary='note_permissions',
        backref='visible_notes',
        lazy='joined'
    )

    def to_dict(self, user=None):
        """Convert note to dictionary for API output.

        Args:
            user: The requesting user (used to determine if permission
                  controls should be included in the response).

        Returns:
            dict: Note data safe for the requesting user to see.
        """
        result = {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'owner_id': self.owner_id,
            'title': self.title,
            'content': self.content,
            'visibility': self.visibility,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z',
        }

        # Only DM/owner sees the permission list
        if user is not None and self.owner_id == user.id:
            result['permitted_user_ids'] = [u.id for u in self.permitted_users]

        return result


# Cross-reference table for per-player note visibility
note_permissions = db.Table(
    'note_permissions',
    db.Column('note_id', db.Integer, db.ForeignKey('notes.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
)
