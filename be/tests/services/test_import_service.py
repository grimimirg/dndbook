"""
Unit tests for ImportService using GIVEN-WHEN-THEN pattern.
"""
import os
import pytest
from app import db
from app.services.import_service import ImportService
from app.models import User


def test_get_import_packages_path(app):
    """GIVEN the ImportService
    WHEN getting the import packages path
    THEN the path should exist and contain 'import-packages'
    """
    with app.app_context():
        # WHEN
        path = ImportService.get_import_packages_path()
        
        # THEN
        assert path is not None
        assert 'import-packages' in path
        assert os.path.exists(path)


def test_import_campaign_no_file(app):
    """GIVEN no file provided
    WHEN attempting to import a campaign
    THEN import should fail with 'No file selected' error
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='No file selected'):
            ImportService.import_campaign(None, user)


def test_import_campaign_empty_filename(app):
    """GIVEN a file with empty filename
    WHEN attempting to import a campaign
    THEN import should fail with 'No file selected' error
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        class MockFile:
            filename = ''
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='No file selected'):
            ImportService.import_campaign(MockFile(), user)
