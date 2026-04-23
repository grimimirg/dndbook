"""Service for importing campaigns from ZIP files."""

import os
import json
import zipfile
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename

from app import db
from app.models import Campaign, Post, Comment, Image, Character, campaign_members


class ImportService:
    """Service class for handling campaign import operations."""
    
    IMPORT_PACKAGES_DIR = 'import-packages'
    
    @staticmethod
    def get_import_packages_path():
        """
        Get the absolute path to the import-packages directory.
        
        Returns:
            str: Absolute path to the import-packages directory
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        import_dir = os.path.join(base_dir, ImportService.IMPORT_PACKAGES_DIR)
        os.makedirs(import_dir, mode=0o755, exist_ok=True)
        return import_dir
    
    @staticmethod
    def import_campaign(file, current_user):
        """
        Import a campaign from an uploaded ZIP file.
        
        Args:
            file: FileStorage object containing the ZIP file
            current_user: User performing the import
            
        Returns:
            list: List of imported campaign dictionaries
            
        Raises:
            ValueError: If file is invalid
            Exception: If import fails
        """
        if not file or file.filename == '':
            raise ValueError('No file selected')
        
        if not file.filename.endswith('.zip'):
            raise ValueError('Only ZIP files are supported')
        
        import_dir = ImportService.get_import_packages_path()
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        safe_filename = secure_filename(file.filename)
        archive_filename = f"{timestamp}_{safe_filename}"
        archive_path = os.path.join(import_dir, archive_filename)
        extract_folder_name = archive_filename.replace('.zip', '')
        extract_path = os.path.join(import_dir, extract_folder_name)
        
        try:
            file.save(archive_path)
            
            os.makedirs(extract_path, mode=0o755, exist_ok=True)
            
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            id_mapping = ImportService._import_data_from_json_files(extract_path, current_user)
            
            db.session.commit()
            
            imported_campaign_ids = list(id_mapping['campaigns'].values())
            imported_campaigns = Campaign.query.filter(Campaign.id.in_(imported_campaign_ids)).all()
            
            shutil.rmtree(extract_path)
            os.remove(archive_path)
            
            return [c.to_dict() for c in imported_campaigns]
            
        except Exception as e:
            db.session.rollback()
            
            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)
            if os.path.exists(archive_path):
                os.remove(archive_path)
            
            raise e
    
    @staticmethod
    def _import_data_from_json_files(extract_path, current_user):
        """
        Import data from JSON files in the correct order.
        
        Args:
            extract_path: Path to the extracted folder
            current_user: User performing the import
            
        Returns:
            dict: Mapping of old IDs to new IDs for each entity type
        """
        id_mapping = {
            'campaigns': {},
            'posts': {},
            'characters': {},
            'images': {},
            'comments': {}
        }
        
        json_files = sorted([f for f in os.listdir(extract_path) if f.endswith('.json')])
        
        for json_file in json_files:
            file_path = os.path.join(extract_path, json_file)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if '01_campaigns.json' in json_file:
                ImportService._import_campaigns(data, current_user, id_mapping)
            elif '02_campaign_members.json' in json_file:
                ImportService._import_campaign_members(data, current_user, id_mapping)
            elif '03_characters.json' in json_file:
                ImportService._import_characters(data, id_mapping)
            elif '04_posts.json' in json_file:
                ImportService._import_posts(data, current_user, id_mapping)
            elif '05_images.json' in json_file:
                ImportService._import_images(data, id_mapping)
            elif '06_comments.json' in json_file:
                ImportService._import_comments(data, current_user, id_mapping)
        
        return id_mapping
    
    @staticmethod
    def _import_campaigns(data, current_user, id_mapping):
        """Import campaigns data."""
        for item in data:
            old_id = item['id']
            campaign = Campaign(
                name=item['name'],
                description=item.get('description', ''),
                owner_id=current_user.id,
                created_at=datetime.fromisoformat(item['created_at']),
                updated_at=datetime.fromisoformat(item['updated_at'])
            )
            db.session.add(campaign)
            db.session.flush()
            id_mapping['campaigns'][old_id] = campaign.id
    
    @staticmethod
    def _import_campaign_members(data, current_user, id_mapping):
        """Import campaign members data."""
        for item in data:
            old_campaign_id = item['campaign_id']
            new_campaign_id = id_mapping['campaigns'].get(old_campaign_id)
            
            if new_campaign_id and item['user_id'] != current_user.id:
                stmt = campaign_members.insert().values(
                    user_id=item['user_id'],
                    campaign_id=new_campaign_id,
                    joined_at=datetime.fromisoformat(item['joined_at']) if item.get('joined_at') else datetime.utcnow()
                )
                db.session.execute(stmt)
    
    @staticmethod
    def _import_characters(data, id_mapping):
        """Import characters data."""
        for item in data:
            old_id = item['id']
            old_campaign_id = item['campaign_id']
            new_campaign_id = id_mapping['campaigns'].get(old_campaign_id)
            
            if new_campaign_id:
                character = Character(
                    campaign_id=new_campaign_id,
                    name=item['name'],
                    race=item['race'],
                    character_class=item['character_class'],
                    description=item.get('description'),
                    image_url=item.get('image_url'),
                    created_at=datetime.fromisoformat(item['created_at']),
                    updated_at=datetime.fromisoformat(item['updated_at'])
                )
                db.session.add(character)
                db.session.flush()
                id_mapping['characters'][old_id] = character.id
    
    @staticmethod
    def _import_posts(data, current_user, id_mapping):
        """Import posts data."""
        for item in data:
            old_id = item['id']
            old_campaign_id = item['campaign_id']
            new_campaign_id = id_mapping['campaigns'].get(old_campaign_id)
            
            if new_campaign_id:
                post = Post(
                    campaign_id=new_campaign_id,
                    author_id=current_user.id,
                    title=item['title'],
                    content=item['content'],
                    created_at=datetime.fromisoformat(item['created_at']),
                    updated_at=datetime.fromisoformat(item['updated_at'])
                )
                db.session.add(post)
                db.session.flush()
                id_mapping['posts'][old_id] = post.id
    
    @staticmethod
    def _import_images(data, id_mapping):
        """Import images data."""
        for item in data:
            old_id = item['id']
            old_post_id = item['post_id']
            new_post_id = id_mapping['posts'].get(old_post_id)
            
            if new_post_id:
                image = Image(
                    post_id=new_post_id,
                    file_path=item['file_path'],
                    order_index=item['order_index'],
                    created_at=datetime.fromisoformat(item['created_at'])
                )
                db.session.add(image)
                db.session.flush()
                id_mapping['images'][old_id] = image.id
    
    @staticmethod
    def _import_comments(data, current_user, id_mapping):
        """Import comments data."""
        for item in data:
            old_id = item['id']
            old_post_id = item['post_id']
            new_post_id = id_mapping['posts'].get(old_post_id)
            
            if new_post_id:
                comment = Comment(
                    post_id=new_post_id,
                    author_id=current_user.id,
                    content=item['content'],
                    created_at=datetime.fromisoformat(item['created_at']),
                    updated_at=datetime.fromisoformat(item['updated_at'])
                )
                db.session.add(comment)
                db.session.flush()
                id_mapping['comments'][old_id] = comment.id
