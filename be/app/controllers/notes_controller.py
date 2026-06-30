from flask import Blueprint, request, jsonify

from app.jwt.jwt_utils import token_required
from app.services.notes_service import NotesService

bp = Blueprint('notes', __name__, url_prefix='/api')


@bp.route('/notes', methods=['GET'])
@token_required
def get_notes(current_user):
    """
    Get notes visible to the current user.

    Optionally filter by owner.

    Query parameters:
        - owner_id (int): Restrict results to a specific owner (optional)

    Args:
        current_user: The authenticated user (injected by token_required decorator)

    Returns:
        JSON response with:
        - 200: List of note objects
    """
    owner_id = request.args.get('owner_id', type=int)
    notes = NotesService.get_notes(user=current_user, owner_id=owner_id)
    return jsonify([n.to_dict() for n in notes]), 200


@bp.route('/notes', methods=['POST'])
@token_required
def create_note(current_user):
    """
    Create a new note.

    Expected JSON payload:
        - title (str): Note title (required)
        - content (str): Markdown content (optional, default: '')
        - visibility (str): 'private' or 'public' (optional, default: 'private')
        - parent_id (int): Parent note ID (optional)

    Args:
        current_user: The authenticated user (injected by token_required decorator)

    Returns:
        JSON response with:
        - 201: Created note data
        - 400: Missing required fields or invalid visibility
        - 404: Parent note not found
    """
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({'error': 'Missing required field: title'}), 400

    try:
        note = NotesService.create_note(
            user=current_user,
            title=data['title'],
            content=data.get('content', ''),
            visibility=data.get('visibility', 'private'),
            parent_id=data.get('parent_id')
        )
        return jsonify(note.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/notes/<int:note_id>', methods=['GET'])
@token_required
def get_note(current_user, note_id):
    """
    Get a specific note by ID.

    The note must be owned by or publicly visible to the current user.

    Args:
        current_user: The authenticated user (injected by token_required decorator)
        note_id (int): The ID of the note

    Returns:
        JSON response with:
        - 200: Note data (with direct children list)
        - 403: User is not authorized to access this note
        - 404: Note not found
    """
    try:
        note = NotesService.get_note(note_id, current_user)
        return jsonify(note.to_dict(include_children=True)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403


@bp.route('/notes/<int:note_id>', methods=['PUT'])
@token_required
def update_note(current_user, note_id):
    """
    Update a note.

    Only the owner can update a note.

    Expected JSON payload (all fields optional):
        - title (str): New note title
        - content (str): New markdown content
        - visibility (str): New visibility ('private' or 'public')
        - parent_id (int): New parent note ID (0 to unset)

    Args:
        current_user: The authenticated user (injected by token_required decorator)
        note_id (int): The ID of the note to update

    Returns:
        JSON response with:
        - 200: Updated note data
        - 400: Invalid field value
        - 403: User is not the owner
        - 404: Note not found
    """
    data = request.get_json()

    try:
        note = NotesService.update_note(
            note_id=note_id,
            user=current_user,
            title=data.get('title') if data else None,
            content=data.get('content') if data else None,
            visibility=data.get('visibility') if data else None,
            parent_id=data.get('parent_id') if data else None
        )
        return jsonify(note.to_dict()), 200
    except ValueError as e:
        status = 400 if any(k in str(e) for k in ('Invalid', 'parent', 'own parent')) else 403
        return jsonify({'error': str(e)}), status


@bp.route('/notes/<int:note_id>', methods=['DELETE'])
@token_required
def delete_note(current_user, note_id):
    """
    Delete a note and all its children.

    Only the owner can delete a note.

    Args:
        current_user: The authenticated user (injected by token_required decorator)
        note_id (int): The ID of the note to delete

    Returns:
        JSON response with:
        - 200: Success message
        - 403: User is not the owner
        - 404: Note not found
    """
    try:
        NotesService.delete_note(note_id, current_user)
        return jsonify({'message': 'Note deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403
