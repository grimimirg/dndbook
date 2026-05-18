"""Service for exporting campaigns to PDF files."""

import os
import base64
from datetime import datetime
from flask import render_template, current_app

from app import db
from app.models import Campaign, Post, Comment, Image
from app.constants.pdf_styles import PdfStyle


class PdfExportService:
    """Service class for handling campaign PDF export operations."""
    
    AVAILABLE_STYLES = PdfStyle.get_all_styles()
    
    @staticmethod
    def export_campaign_to_pdf(campaign, current_user, style_name='classic'):
        """
        Export a campaign to PDF with custom styling.
        
        Args:
            campaign: Campaign object to export
            current_user: User performing the export
            style_name: Name of the PDF style template (classic, dark, fantasy)
            
        Returns:
            tuple: (pdf_filepath, cleanup_callback) where cleanup_callback is a function
                   to call after sending the file
                   
        Raises:
            ValueError: If style_name is not valid
            Exception: If export fails
        """
        if style_name not in PdfExportService.AVAILABLE_STYLES:
            raise ValueError(f'Invalid style. Available styles: {PdfExportService.AVAILABLE_STYLES}')
        
        # Create temp directory for PDF export
        temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'pdf_exports')
        os.makedirs(temp_dir, mode=0o755, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        safe_campaign_name = campaign.name.replace(' ', '_').replace('/', '_')
        pdf_filename = f"{safe_campaign_name}_{timestamp}.pdf"
        pdf_filepath = os.path.join(temp_dir, pdf_filename)
        
        try:
            # Fetch campaign data
            campaign_data = PdfExportService._get_campaign_data(campaign)
            
            # Fetch posts with comments and images, ordered as in feed
            posts_data = PdfExportService._get_posts_data(campaign.id)
            
            # Render HTML template
            html_content = render_template(
                'campaign_pdf.html',
                campaign=campaign_data,
                posts=posts_data,
                style=style_name
            )
            
            # Convert HTML to PDF using WeasyPrint
            from weasyprint import HTML, CSS
            
            # Load CSS based on style
            css_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'fe', 'src', 'pdf-styles', f'{style_name}.css'
            )
            
            html_obj = HTML(string=html_content, base_url='')
            css_obj = CSS(filename=css_path) if os.path.exists(css_path) else None
            
            html_obj.write_pdf(pdf_filepath, stylesheets=[css_obj] if css_obj else None)
            
            def cleanup():
                """Cleanup function to remove the PDF file after sending."""
                try:
                    if os.path.exists(pdf_filepath):
                        os.remove(pdf_filepath)
                except Exception:
                    pass
            
            return pdf_filepath, cleanup
            
        except Exception as e:
            if os.path.exists(pdf_filepath):
                os.remove(pdf_filepath)
            raise e
    
    @staticmethod
    def _get_campaign_data(campaign):
        """Get campaign data for PDF export."""
        return {
            'name': campaign.name,
            'description': campaign.description
        }
    
    @staticmethod
    def _get_posts_data(campaign_id):
        """
        Get posts with comments and images, ordered as in feed.
        
        Returns list of posts with:
        - title, content, author
        - images with file paths and descriptions
        - comments ordered by created_at
        """
        # Get posts ordered by post_order (custom order) or created_at
        posts = Post.query.filter_by(campaign_id=campaign_id)\
            .order_by(Post.post_order.asc().nulls_last(), Post.created_at.asc())\
            .all()
        
        posts_data = []
        
        for post in posts:
            # Get images for this post
            images = Image.query.filter_by(post_id=post.id)\
                .order_by(Image.order_index.asc())\
                .all()
            
            # Get comments for this post
            comments = Comment.query.filter_by(post_id=post.id)\
                .order_by(Comment.created_at.asc())\
                .all()
            
            # Convert images to base64 for PDF embedding
            images_data = []
            for img in images:
                image_data = {
                    'order_index': img.order_index,
                    'description': getattr(img, 'description', '')
                }
                
                # Try to read image file and convert to base64
                try:
                    if img.file_path and os.path.exists(img.file_path):
                        with open(img.file_path, 'rb') as f:
                            image_data['data'] = base64.b64encode(f.read()).decode('utf-8')
                            image_data['mime_type'] = PdfExportService._get_mime_type(img.file_path)
                except Exception as e:
                    current_app.logger.warning(f"Failed to read image {img.file_path}: {e}")
                
                images_data.append(image_data)
            
            # Convert comments to dict
            comments_data = []
            for comment in comments:
                comments_data.append({
                    'author': comment.author.username if comment.author else 'Unknown',
                    'content': comment.content,
                    'created_at': comment.created_at
                })
            
            posts_data.append({
                'title': post.title,
                'content': post.content,
                'author': post.author.username if post.author else 'Unknown',
                'images': images_data,
                'comments': comments_data
            })
        
        return posts_data
    
    @staticmethod
    def _get_mime_type(file_path):
        """Get MIME type based on file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return mime_types.get(ext, 'image/jpeg')
