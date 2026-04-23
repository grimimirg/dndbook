"""Controller for campaign import operations."""

from flask import Blueprint, request, jsonify, current_app

from app.jwt.jwt_utils import token_required
from app.services.import_service import ImportService

bp = Blueprint('import', __name__, url_prefix='/api/import')


@bp.route('', methods=['POST'])
@token_required
def import_campaign(current_user):
    """
    Import a campaign from an uploaded ZIP file.
    
    The import process:
    1. Upload and save the ZIP file
    2. Extract to a temporary folder
    3. Import JSON files in the correct order
    4. Cleanup (delete extracted folder and ZIP file)
    
    Expected file upload:
        - archive: ZIP file containing campaign data
        
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        
    Returns:
        JSON response with:
        - 200: Success message with imported campaign details
        - 400: No file uploaded or invalid file
        - 500: Import failed
    """
    if 'archive' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['archive']
    
    try:
        imported_campaigns = ImportService.import_campaign(file, current_user)
        
        return jsonify({
            'message': 'Campaign imported successfully',
            'campaigns': imported_campaigns
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Import failed: {e}")
        return jsonify({'error': f'Import failed: {str(e)}'}), 500
