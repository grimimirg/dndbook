"""Service for exporting campaigns to ZIP files."""

import os
import json
import zipfile
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename

from app import db
from app.models import Campaign, Post, Comment, Image, Character, CampaignMembers


class ExportService:
    """Service class for handling campaign export operations."""
    
    IMPORT_PACKAGES_DIR = 'import-packages'
    
    @staticmethod
    def get_import_packages_path():
        """
        Get the absolute path to the import-packages directory.
        
        Returns:
            str: Absolute path to the import-packages directory
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        import_dir = os.path.join(base_dir, ExportService.IMPORT_PACKAGES_DIR)
        os.makedirs(import_dir, mode=0o755, exist_ok=True)
        return import_dir
    
    @staticmethod
    def export_campaign(campaign, current_user):
        """
        Export a campaign and all its related data to a ZIP file.
        
        Args:
            campaign: Campaign object to export
            current_user: User performing the export
            
        Returns:
            tuple: (zip_filepath, cleanup_callback) where cleanup_callback is a function
                   to call after sending the file
                   
        Raises:
            PermissionError: If user is not the campaign owner
            Exception: If export fails
        """
        if campaign.owner_id != current_user.id:
            raise PermissionError('Only campaign owner can export campaigns')
        
        import_dir = ExportService.get_import_packages_path()
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        safe_campaign_name = secure_filename(campaign.name.replace(' ', '_'))
        export_folder_name = f"{safe_campaign_name}_{timestamp}"
        export_folder_path = os.path.join(import_dir, export_folder_name)
        zip_filepath = None
        
        try:
            os.makedirs(export_folder_path, mode=0o755, exist_ok=True)
            
            ExportService._export_campaign_data(campaign, export_folder_path)
            ExportService._export_members_data(campaign.id, export_folder_path)
            ExportService._export_characters_data(campaign.id, export_folder_path)
            ExportService._export_posts_data(campaign.id, export_folder_path)
            ExportService._export_images_data(campaign.id, export_folder_path)
            ExportService._export_comments_data(campaign.id, export_folder_path)
            
            zip_filename = f"{export_folder_name}.zip"
            zip_filepath = os.path.join(import_dir, zip_filename)
            
            ExportService._create_zip(export_folder_path, zip_filepath)
            
            shutil.rmtree(export_folder_path)
            
            def cleanup():
                """Cleanup function to remove the ZIP file after sending."""
                try:
                    if os.path.exists(zip_filepath):
                        os.remove(zip_filepath)
                except Exception:
                    pass
            
            return zip_filepath, cleanup
            
        except Exception as e:
            if export_folder_path and os.path.exists(export_folder_path):
                shutil.rmtree(export_folder_path)
            if zip_filepath and os.path.exists(zip_filepath):
                os.remove(zip_filepath)
            raise e
    
    @staticmethod
    def _export_campaign_data(campaign, export_folder_path):
        """Export campaign data to JSON file."""
        campaign_data = {
            'id': campaign.id,
            'name': campaign.name,
            'description': campaign.description,
            'owner_id': campaign.owner_id,
            'created_at': campaign.created_at.isoformat(),
            'updated_at': campaign.updated_at.isoformat()
        }
        
        with open(os.path.join(export_folder_path, '01_campaigns.json'), 'w', encoding='utf-8') as f:
            json.dump([campaign_data], f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def _export_members_data(campaign_id, export_folder_path):
        """Export campaign members data to JSON file."""
        members_data = []
        stmt = db.select(CampaignMembers).where(CampaignMembers.c.campaign_id == campaign_id)
        members_result = db.session.execute(stmt).fetchall()
        
        for member in members_result:
            members_data.append({
                'user_id': member.user_id,
                'campaign_id': member.campaign_id,
                'joined_at': member.joined_at.isoformat() if member.joined_at else None
            })
        
        with open(os.path.join(export_folder_path, '02_campaign_members.json'), 'w', encoding='utf-8') as f:
            json.dump(members_data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def _export_characters_data(campaign_id, export_folder_path):
        """Export characters data to JSON file."""
        characters = Character.query.filter_by(campaign_id=campaign_id).all()
        characters_data = []
        
        for char in characters:
            characters_data.append({
                'id': char.id,
                'campaign_id': char.campaign_id,
                'name': char.name,
                'race': char.race,
                'character_class': char.character_class,
                'description': char.description,
                'image_url': char.image_url,
                'created_at': char.created_at.isoformat(),
                'updated_at': char.updated_at.isoformat()
            })
        
        with open(os.path.join(export_folder_path, '03_characters.json'), 'w', encoding='utf-8') as f:
            json.dump(characters_data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def _export_posts_data(campaign_id, export_folder_path):
        """Export posts data to JSON file."""
        posts = Post.query.filter_by(campaign_id=campaign_id).all()
        posts_data = []
        
        for post in posts:
            posts_data.append({
                'id': post.id,
                'campaign_id': post.campaign_id,
                'author_id': post.author_id,
                'title': post.title,
                'content': post.content,
                'created_at': post.created_at.isoformat(),
                'updated_at': post.updated_at.isoformat()
            })
        
        with open(os.path.join(export_folder_path, '04_posts.json'), 'w', encoding='utf-8') as f:
            json.dump(posts_data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def _export_images_data(campaign_id, export_folder_path):
        """Export images data to JSON file."""
        posts = Post.query.filter_by(campaign_id=campaign_id).all()
        post_ids = [post.id for post in posts]
        images_data = []
        
        if post_ids:
            images = Image.query.filter(Image.post_id.in_(post_ids)).all()
            for img in images:
                images_data.append({
                    'id': img.id,
                    'post_id': img.post_id,
                    'file_path': img.file_path,
                    'order_index': img.order_index,
                    'created_at': img.created_at.isoformat()
                })
        
        with open(os.path.join(export_folder_path, '05_images.json'), 'w', encoding='utf-8') as f:
            json.dump(images_data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def _export_comments_data(campaign_id, export_folder_path):
        """Export comments data to JSON file."""
        posts = Post.query.filter_by(campaign_id=campaign_id).all()
        post_ids = [post.id for post in posts]
        comments_data = []
        
        if post_ids:
            comments = Comment.query.filter(Comment.post_id.in_(post_ids)).all()
            for comment in comments:
                comments_data.append({
                    'id': comment.id,
                    'post_id': comment.post_id,
                    'author_id': comment.author_id,
                    'content': comment.content,
                    'created_at': comment.created_at.isoformat(),
                    'updated_at': comment.updated_at.isoformat()
                })
        
        with open(os.path.join(export_folder_path, '06_comments.json'), 'w', encoding='utf-8') as f:
            json.dump(comments_data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def _create_zip(source_folder, zip_filepath):
        """
        Create a ZIP file from a folder.
        
        Args:
            source_folder: Path to the folder to zip
            zip_filepath: Path where the ZIP file will be created
        """
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_folder)
                    zipf.write(file_path, arcname)
