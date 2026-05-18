"""Controller for campaign PDF export operations."""

import os
from flask import Blueprint, jsonify, current_app, request, send_file

from app.jwt.jwt_utils import token_required
from app.models import Campaign
from app.services.pdf_export_service import PdfExportService
from app.constants.pdf_styles import PdfStyle

bp = Blueprint('pdf_export', __name__, url_prefix='/api/pdf-export')


@bp.route('/<int:campaign_id>', methods=['GET'])
@token_required
def export_campaign_to_pdf(current_user, campaign_id):
    """
    Export a campaign to PDF with custom styling.
    
    Any authenticated user can export the campaign to PDF.
    The PDF contains the campaign description and all posts with comments,
    ordered as they appear in the feed.
    
    Query Parameters:
        style (str): PDF style template (classic, dark, fantasy). Default: classic
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign to export
        
    Returns:
        PDF file download
        - 404: Campaign not found
        - 400: Invalid style parameter
        - 500: Export failed
    """
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Get style from query parameters
    style = request.args.get('style', PdfStyle.CLASSIC.value)
    
    # Validate style
    if not PdfStyle.is_valid(style):
        return jsonify({'error': f'Invalid style. Available styles: {PdfStyle.get_all_styles()}'}), 400
    
    try:
        pdf_filepath, cleanup = PdfExportService.export_campaign_to_pdf(
            campaign, current_user, style
        )
        
        response = send_file(
            pdf_filepath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=os.path.basename(pdf_filepath)
        )
        
        @response.call_on_close
        def cleanup_wrapper():
            try:
                cleanup()
            except Exception as e:
                current_app.logger.error(f"Failed to cleanup PDF export file: {e}")
        
        return response
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"PDF export failed: {e}")
        return jsonify({'error': f'PDF export failed: {str(e)}'}), 500
