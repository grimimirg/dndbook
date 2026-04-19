from datetime import datetime

from app import db


class CampaignInvite(db.Model):
    """
    CampaignInvite model representing invitations to join campaigns.
    
    Tracks invites sent from one user to another for a specific campaign.
    """
    __tablename__ = 'campaign_invites'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    inviter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)

    campaign = db.relationship('Campaign', backref=db.backref('invites', lazy=True, cascade='all, delete-orphan'))

    def to_dict(self):
        """
        Convert campaign invite object to dictionary representation.
        
        Returns:
            dict: Invite data with campaign and user information
        """
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'campaign_name': self.campaign.name if self.campaign else None,
            'inviter_id': self.inviter_id,
            'inviter_username': self.inviter.username if self.inviter else None,
            'invitee_id': self.invitee_id,
            'invitee_username': self.invitee.username if self.invitee else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'responded_at': self.responded_at.isoformat() if self.responded_at else None
        }
