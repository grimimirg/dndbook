"""Controller for campaign export operations."""

import os
from flask import Blueprint, jsonify, current_app, send_file

from app.jwt.jwt_utils import token_required
from app.models import Campaign
from app.services.export_service import ExportService

bp = Blueprint('export', __name__, url_prefix='/api/export')


@bp.route('/<int:campaign_id>', methods=['GET'])
@token_required
def export_campaign(current_user, campaign_id):
    """
    Export a campaign and all its related data as a ZIP file.
    
    Only the campaign owner can export the campaign.
    The ZIP contains JSON files for each table, prefixed with import order numbers.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign to export
        
    Returns:
        ZIP file download with campaign data
        - 403: User is not the campaign owner
        - 404: Campaign not found
        - 500: Export failed
    """
    campaign = Campaign.query.get_or_404(campaign_id)
    
    try:
        zip_filepath, cleanup = ExportService.export_campaign(campaign, current_user)
        
        response = send_file(
            zip_filepath,
            mimetype='application/zip',
            as_attachment=True,
            download_name=os.path.basename(zip_filepath)
        )
        
        @response.call_on_close
        def cleanup_wrapper():
            try:
                cleanup()
            except Exception as e:
                current_app.logger.error(f"Failed to cleanup export file: {e}")
        
        return response
        
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        current_app.logger.error(f"Export failed: {e}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500
