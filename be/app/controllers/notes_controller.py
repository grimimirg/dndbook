"""Controller for note CRUD endpoints with authorization."""

from flask import Blueprint, request, jsonify

from app.jwt.jwt_utils import token_required
from app.services.notes_service import NotesService

bp = Blueprint("notes", __name__, url_prefix="/api")


@bp.route("/campaigns/<int:campaign_id>/notes", methods=["GET"])
@token_required
def get_notes(current_user, campaign_id):
    """Get notes visible to the current user in a campaign.

    DM/owner sees all notes; players see only notes they are permitted to view.

    Args:
        current_user: Authenticated user (injected by token_required)
        campaign_id (int): Campaign ID

    Returns:
        200: List of visible notes
        403: User is not authorized to access this campaign
        404: Campaign not found
    """
    try:
        notes = NotesService.get_notes(campaign_id, current_user)
        return jsonify(notes), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 403


@bp.route("/campaigns/<int:campaign_id>/notes", methods=["POST"])
@token_required
def create_note(current_user, campaign_id):
    """Create a new note. Only campaign owner (DM) can create notes.

    Expected JSON payload:
        - title (str): Note title (required)
        - content (str): Markdown content (optional)
        - visibility (str): "personal" or "players" (optional, default: "personal")
        - parent_id (int): Parent note ID for nesting (optional)

    Args:
        current_user: Authenticated user
        campaign_id (int): Campaign ID

    Returns:
        201: Created note data
        400: Missing or invalid fields
        403: User is not authorized
    """
    data = request.get_json() or {}

    if not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    try:
        note = NotesService.create_note(
            user=current_user,
            campaign_id=campaign_id,
            title=data["title"],
            content=data.get("content", ""),
            visibility=data.get("visibility", "personal"),
            parent_id=data.get("parent_id"),
        )
        return jsonify(note.to_dict(user=current_user)), 201
    except ValueError as e:
        if any(x in str(e) for x in ("Title", "visibility", "Parent")):
            return jsonify({"error": str(e)}), 400
        return jsonify({"error": str(e)}), 403


@bp.route("/notes/<int:note_id>", methods=["GET"])
@token_required
def get_note(current_user, note_id):
    """Get a single note by ID.

    Args:
        current_user: Authenticated user
        note_id (int): Note ID

    Returns:
        200: Note data
        403: User is not authorized to view this note
        404: Note not found
    """
    try:
        note = NotesService.get_note(note_id, current_user)
        return jsonify(note), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 403


@bp.route("/notes/<int:note_id>", methods=["PUT"])
@token_required
def update_note(current_user, note_id):
    """Update a note. Only campaign owner (DM) can update.

    Expected JSON payload:
        - title (str): Updated title (optional)
        - content (str): Updated markdown content (optional)
        - visibility (str): "personal" or "players" (optional)
        - parent_id (int): Updated parent note ID (optional)

    Args:
        current_user: Authenticated user
        note_id (int): Note ID

    Returns:
        200: Updated note data
        400: Invalid fields
        403: User is not authorized
    """
    data = request.get_json() or {}

    try:
        note = NotesService.update_note(
            note_id=note_id,
            user=current_user,
            title=data.get("title"),
            content=data.get("content"),
            visibility=data.get("visibility"),
            parent_id=data.get("parent_id"),
        )
        return jsonify(note.to_dict(user=current_user)), 200
    except ValueError as e:
        if any(
            x in str(e) for x in ("Title", "visibility", "Parent", "cannot be empty")
        ):
            return jsonify({"error": str(e)}), 400
        return jsonify({"error": str(e)}), 403


@bp.route("/notes/<int:note_id>", methods=["DELETE"])
@token_required
def delete_note(current_user, note_id):
    """Delete a note. Only campaign owner (DM) can delete.

    Args:
        current_user: Authenticated user
        note_id (int): Note ID

    Returns:
        200: Success message
        403: User is not authorized
    """
    try:
        NotesService.delete_note(note_id, current_user)
        return jsonify({"message": "Note deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 403


@bp.route("/notes/<int:note_id>/permissions", methods=["PUT"])
@token_required
def set_note_permissions(current_user, note_id):
    """Set which players can view a players-visibility note.

    Only the campaign owner (DM) can set permissions.
    Replaces any existing permission set with the provided list.

    Expected JSON payload:
        - user_ids (list): List of user IDs to grant access

    Args:
        current_user: Authenticated user
        note_id (int): Note ID

    Returns:
        200: Updated note data
        400: Invalid payload
        403: User is not authorized
    """
    data = request.get_json() or {}

    if "user_ids" not in data or not isinstance(data["user_ids"], list):
        return jsonify({"error": "user_ids must be an array"}), 400

    try:
        note = NotesService.set_note_permissions(
            note_id=note_id,
            user=current_user,
            user_ids=data["user_ids"],
        )
        return jsonify(note.to_dict(user=current_user)), 200
    except ValueError as e:
        if any(x in str(e) for x in ("not found", "not a member", "Permissions only")):
            return jsonify({"error": str(e)}), 400
        return jsonify({"error": str(e)}), 403
