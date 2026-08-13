"""Service for note operations with per-player authorization."""

from app import db
from app.models import Campaign, Note, note_permissions
from app.services.posts_service import PostsService


class NotesService:
    """Service for handling note CRUD and authorization."""

    @staticmethod
    def can_manage_notes(campaign, user):
        """Check if user can manage notes (DM/owner only)."""
        return campaign.owner_id == user.id

    @staticmethod
    def can_view_note(note, user):
        """Check if a user can view a specific note.

        Personal notes: only the owner (DM) can view.
        Player notes: owner + explicitly permitted players can view.
        """
        if note.owner_id == user.id:
            return True
        if note.visibility == "personal":
            return False
        permitted_ids = {u.id for u in note.permitted_users}
        return user.id in permitted_ids

    @staticmethod
    def get_notes(campaign_id, user):
        """Get all notes visible to a user within a campaign."""
        campaign = Campaign.query.get_or_404(campaign_id)
        if not PostsService.can_access_campaign(campaign, user):
            raise ValueError("Unauthorized")

        if NotesService.can_manage_notes(campaign, user):
            notes = Note.query.filter_by(campaign_id=campaign_id).order_by(
                Note.created_at.desc()
            ).all()
        else:
            notes = (
                Note.query
                .filter_by(campaign_id=campaign_id, visibility="players")
                .filter(Note.permitted_users.any(id=user.id))
                .order_by(Note.created_at.desc())
                .all()
            )

        return [note.to_dict(user=user) for note in notes]

    @staticmethod
    def get_note(note_id, user):
        """Get a single note by ID with authorization check."""
        note = Note.query.get_or_404(note_id)
        if not NotesService.can_view_note(note, user):
            raise ValueError("Unauthorized")
        return note.to_dict(user=user)

    @staticmethod
    def create_note(user, campaign_id, title, content="", visibility="personal",
                    parent_id=None):
        """Create a new note. Only campaign owner can create."""
        campaign = Campaign.query.get_or_404(campaign_id)
        if not NotesService.can_manage_notes(campaign, user):
            raise ValueError("Unauthorized")
        if not title:
            raise ValueError("Title is required")
        if visibility not in ("personal", "players"):
            raise ValueError("visibility must be personal or players")
        if parent_id is not None:
            parent = Note.query.get(parent_id)
            if parent is None or parent.campaign_id != campaign_id:
                raise ValueError("Parent note not found in this campaign")

        note = Note(
            campaign_id=campaign_id,
            owner_id=user.id,
            title=title,
            content=content,
            visibility=visibility,
            parent_id=parent_id,
        )
        db.session.add(note)
        db.session.commit()
        db.session.refresh(note)
        return note

    @staticmethod
    def update_note(note_id, user, title=None, content=None, visibility=None,
                    parent_id=None):
        """Update a note. Only campaign owner can update."""
        note = Note.query.get_or_404(note_id)
        campaign = Campaign.query.get(note.campaign_id)
        if not NotesService.can_manage_notes(campaign, user):
            raise ValueError("Unauthorized")

        if title is not None:
            if not title:
                raise ValueError("Title cannot be empty")
            note.title = title
        if content is not None:
            note.content = content
        if visibility is not None:
            if visibility not in ("personal", "players"):
                raise ValueError("visibility must be personal or players")
            note.visibility = visibility
        if parent_id is not None:
            parent = Note.query.get(parent_id)
            if parent is None or parent.campaign_id != note.campaign_id:
                raise ValueError("Parent note not found")
            note.parent_id = parent_id

        db.session.commit()
        return note

    @staticmethod
    def delete_note(note_id, user):
        """Delete a note. Only campaign owner can delete."""
        note = Note.query.get_or_404(note_id)
        campaign = Campaign.query.get(note.campaign_id)
        if not NotesService.can_manage_notes(campaign, user):
            raise ValueError("Unauthorized")
        db.session.delete(note)
        db.session.commit()

    @staticmethod
    def set_note_permissions(note_id, user, user_ids):
        """Set which players can view a players-visibility note.

        Only the campaign owner (DM) can set permissions.
        Replaces existing permissions with the given user list.
        """
        note = Note.query.get_or_404(note_id)
        campaign = Campaign.query.get(note.campaign_id)
        if not NotesService.can_manage_notes(campaign, user):
            raise ValueError("Unauthorized")
        if note.visibility != "players":
            raise ValueError("Permissions only for players-visibility notes")

        from app.models import User as UserModel
        users = UserModel.query.filter(UserModel.id.in_(user_ids)).all()
        found_ids = {u.id for u in users}

        for uid in user_ids:
            if uid not in found_ids:
                raise ValueError(f"User {uid} not found")
            is_member = campaign.members.filter_by(id=uid).first() is not None
            if uid != campaign.owner_id and not is_member:
                raise ValueError(f"User {uid} is not a campaign member")

        note.permitted_users = users
        db.session.commit()
        return note
