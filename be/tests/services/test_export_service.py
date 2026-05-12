"""
Unit tests for ExportService using GIVEN-WHEN-THEN pattern.
"""
import pytest
import os
from app import db
from app.services.export_service import ExportService
from app.models import Campaign, User


def test_get_import_packages_path(app):
    """GIVEN the ExportService
    WHEN getting the import packages path
    THEN the path should exist and contain 'import-packages'
    """
    with app.app_context():
        # WHEN
        path = ExportService.get_import_packages_path()
        
        # THEN
        assert path is not None
        assert 'import-packages' in path
        assert os.path.exists(path)


def test_export_campaign_as_owner(app):
    """GIVEN a campaign owned by a user
    WHEN the owner exports the campaign
    THEN a ZIP file should be created and cleanup should work
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=user.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        # WHEN
        zip_filepath, cleanup = ExportService.export_campaign(campaign, user)
        
        # THEN
        assert zip_filepath is not None
        assert zip_filepath.endswith('.zip')
        assert os.path.exists(zip_filepath)
        
        # Cleanup
        cleanup()
        assert not os.path.exists(zip_filepath)


def test_export_campaign_unauthorized(app):
    """GIVEN a campaign owned by one user
    WHEN another user attempts to export it
    THEN export should be denied with PermissionError
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        other = User(username='other', email='other@example.com')
        other.set_password('password123')
        db.session.add(other)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=owner.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        # WHEN & THEN
        with pytest.raises(PermissionError, match='Only campaign owner can export campaigns'):
            ExportService.export_campaign(campaign, other)
