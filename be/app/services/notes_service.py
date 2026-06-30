"""Service for note operations."""

from app import db
from app.models.note import Note


class NotesService:
    """Service for handling note business logic."""

    @staticmethod
    def can_read(note, user):
        """
        Check if a user can read a note.

        Args:
            note (Note): The note to check
            user: The requesting user

        Returns:
            bool: True if the user is the owner or the note is public
        """
        return note.owner_id == user.id or note.visibility == Note.VISIBILITY_PUBLIC

    @staticmethod
    def can_write(note, user):
        """
        Check if a user can modify or delete a note.

        Args:
            note (Note): The note to check
            user: The requesting user

        Returns:
            bool: True only if the user is the owner
        """
        return note.owner_id == user.id

    @staticmethod
    def create_note(user, title, content='', visibility=Note.VISIBILITY_PRIVATE, parent_id=None):
        """
        Create a new note.

        Args:
            user: The authenticated owner
            title (str): Note title
            content (str): Markdown content
            visibility (str): 'private' or 'public' (default: 'private')
            parent_id (int|None): Optional parent note ID

        Returns:
            Note: The created note

        Raises:
            ValueError: If visibility is invalid or parent note not accessible
        """
        if visibility not in Note.ALLOWED_VISIBILITIES:
            raise ValueError(f"Invalid visibility '{visibility}'. Allowed: {sorted(Note.ALLOWED_VISIBILITIES)}")

        if parent_id is not None:
            parent = Note.query.get(parent_id)
            if parent is None:
                raise ValueError('Parent note not found')
            if not NotesService.can_read(parent, user):
                raise ValueError('Unauthorized')

        note = Note(
            title=title,
            content=content,
            owner_id=user.id,
            visibility=visibility,
            parent_id=parent_id
        )
        db.session.add(note)
        db.session.commit()
        return note

    @staticmethod
    def get_notes(user, owner_id=None):
        """
        Return notes visible to the requesting user.

        - Without owner_id filter: returns the user's own notes plus all public notes.
        - With owner_id filter: returns that owner's notes that are visible to the requesting user.

        Args:
            user: The authenticated requesting user
            owner_id (int|None): Optionally restrict to a specific owner

        Returns:
            list[Note]: List of accessible notes
        """
        if owner_id is not None:
            if owner_id == user.id:
                notes = Note.query.filter_by(owner_id=owner_id).all()
            else:
                notes = Note.query.filter_by(owner_id=owner_id, visibility=Note.VISIBILITY_PUBLIC).all()
        else:
            from sqlalchemy import or_
            notes = Note.query.filter(
                or_(Note.owner_id == user.id, Note.visibility == Note.VISIBILITY_PUBLIC)
            ).all()
        return notes

    @staticmethod
    def get_note(note_id, user):
        """
        Get a specific note by ID.

        Args:
            note_id (int): The note ID
            user: The authenticated requesting user

        Returns:
            Note: The note object

        Raises:
            ValueError: If not found or user is not authorized to read it
        """
        note = Note.query.get_or_404(note_id)
        if not NotesService.can_read(note, user):
            raise ValueError('Unauthorized')
        return note

    @staticmethod
    def update_note(note_id, user, title=None, content=None, visibility=None, parent_id=None):
        """
        Update a note.

        Only the owner can update a note.

        Args:
            note_id (int): The note ID
            user: The authenticated requesting user
            title (str|None): New title
            content (str|None): New markdown content
            visibility (str|None): New visibility value
            parent_id (int|None|sentinel): Pass -1 to explicitly unset parent

        Returns:
            Note: The updated note

        Raises:
            ValueError: If not found, user is not the owner, or validation fails
        """
        note = Note.query.get_or_404(note_id)
        if not NotesService.can_write(note, user):
            raise ValueError('Unauthorized')

        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
        if visibility is not None:
            if visibility not in Note.ALLOWED_VISIBILITIES:
                raise ValueError(f"Invalid visibility '{visibility}'. Allowed: {sorted(Note.ALLOWED_VISIBILITIES)}")
            note.visibility = visibility
        if parent_id is not None:
            if parent_id == 0:
                note.parent_id = None
            else:
                parent = Note.query.get(parent_id)
                if parent is None:
                    raise ValueError('Parent note not found')
                if not NotesService.can_read(parent, user):
                    raise ValueError('Unauthorized')
                if parent_id == note_id:
                    raise ValueError('A note cannot be its own parent')
                note.parent_id = parent_id

        db.session.commit()
        return note

    @staticmethod
    def delete_note(note_id, user):
        """
        Delete a note and its children (cascade).

        Only the owner can delete a note.

        Args:
            note_id (int): The note ID
            user: The authenticated requesting user

        Raises:
            ValueError: If not found or user is not the owner
        """
        note = Note.query.get_or_404(note_id)
        if not NotesService.can_write(note, user):
            raise ValueError('Unauthorized')
        db.session.delete(note)
        db.session.commit()
