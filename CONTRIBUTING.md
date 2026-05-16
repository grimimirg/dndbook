# Contributing to D&D Book

Thank you for your interest in contributing to D&D Book! This document provides technical instructions for developers who want to contribute to the project.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Architecture](#project-architecture)
- [Database Migrations](#database-migrations)
- [Adding a New Language](#adding-a-new-language)
- [Creating a New API Endpoint](#creating-a-new-api-endpoint)
- [Writing Tests](#writing-tests)
- [Code Style Guidelines](#code-style-guidelines)
- [Submitting Changes](#submitting-changes)

---

## Development Setup

### Prerequisites

- Python 3.8+
- Node.js 18+
- Docker (for PostgreSQL database)

### Backend Development

1. Navigate to the backend directory:
   ```bash
   cd be
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Start the backend:
   ```bash
   ./run-standalone.sh
   ```

The backend will be available at `http://localhost:5000`

### Frontend Development

1. Navigate to the frontend directory:
   ```bash
   cd fe
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Start the frontend:
   ```bash
   ./run-standalone.sh
   ```

The frontend will be available at `http://localhost:5173`

---

## Project Architecture

D&D Book follows a clean three-layer architecture with clear separation of concerns:

### Backend Structure (Python/Flask)

```
be/
├── app/
│   ├── controllers/     # HTTP request handlers
│   ├── services/        # Business logic layer
│   ├── models/          # Data models (SQLAlchemy)
│   ├── jwt/             # JWT authentication utilities
│   └── events/          # WebSocket events
├── tests/
│   ├── conftest.py      # Pytest configuration and fixtures
│   └── services/        # Service layer tests
└── main.py              # Application entry point
```

### Frontend Structure (Vue.js)

```
fe/
├── src/
│   ├── composables/     # Vue composition functions
│   ├── config/          # Configuration files
│   ├── constants/       # Application constants
│   ├── locales/         # i18n translation files (YAML)
│   ├── router/          # Vue Router configuration
│   ├── services/        # API service layer
│   ├── stores/          # Pinia state management
│   ├── views/           # Page components
│   ├── i18n.js          # i18n configuration
│   └── main.js          # Application entry point
```

### Layer Responsibilities

**Controllers (`be/app/controllers/`):**
- Handle HTTP requests and responses
- Validate incoming data
- Call service layer for business logic
- Return appropriate HTTP status codes and JSON responses

**Services (`be/app/services/`):**
- Contain business logic
- Interact with database through models
- Perform data transformations
- Handle validation and error handling

**Models (`be/app/models/`):**
- Define database schema using SQLAlchemy
- Represent data structures
- Include relationships between entities
- Provide helper methods (e.g., `to_dict()`, password hashing)

---

## Database Migrations

D&D Book uses Flask-Migrate (a wrapper around Alembic) for database schema management. This approach provides version control for your database schema, allowing for safe and reversible schema changes in production environments.

### Why Flask-Migrate?

- **Version Control**: Track every schema change over time
- **Safe Upgrades**: Apply changes incrementally without data loss
- **Rollback Capability**: Revert changes if something goes wrong
- **Team Collaboration**: Multiple developers can work on schema changes safely
- **Production Ready**: Essential for managing database changes in production

### Migration Workflow

When you modify database models (add/remove columns, change relationships, etc.), you must create and apply a migration:

#### Step 1: Modify the Model

Make your changes to the model files in `be/app/models/`. For example, adding a new column:

```python
# In be/app/models/user.py
class User(db.Model):
    # ... existing fields ...
    bio = db.Column(db.Text)  # New field
```

#### Step 2: Generate a Migration

Create a migration file that captures the schema changes:

```bash
cd /dndbook/be
source venv/bin/activate  # Activate virtual environment
flask db migrate -m "Add bio field to users table"
```

This will create a new migration file in `migrations/versions/` with a descriptive name.

**Important**: Always review the generated migration file to ensure it captures your intended changes correctly.

#### Step 3: Apply the Migration

Apply the migration to your database:

```bash
flask db upgrade
```

This runs the SQL commands to update your database schema.

#### Step 4: Test Locally

Verify that your application works with the new schema:

```bash
./run-standalone.sh  # Or your preferred development startup method
```

### Migration Commands

| Command | Purpose |
|---------|---------|
| `flask db migrate -m "message"` | Generate a new migration based on model changes |
| `flask db upgrade` | Apply pending migrations to the database |
| `flask db downgrade` | Revert the last migration |
| `flask db current` | Show the current migration version |
| `flask db history` | Show migration history |
| `flask db revision -m "message"` | Create an empty migration file (for manual SQL) |

### Rollback Procedure

If you need to revert a migration:

```bash
# Revert the last migration
flask db downgrade

# Revert multiple migrations
flask db downgrade -2  # Revert last 2 migrations
```

**Warning**: Only rollback migrations in development. In production, create a new migration to fix issues instead of rolling back.

### Docker and Migrations

When running with Docker, migrations are automatically applied during container startup:

1. **init-and-start.sh** applies migrations on container initialization
2. **main.py** applies migrations as a safety check before starting the application

This ensures that the database schema is always up-to-date, even if you skip the init script.

### Best Practices

1. **Review Generated Migrations**: Always check the generated migration file to ensure it matches your intentions
2. **Descriptive Messages**: Use clear, descriptive migration messages (e.g., "Add email uniqueness constraint" not "Update user model")
3. **One Change Per Migration**: Keep migrations focused on a single schema change
4. **Test Before Deploying**: Always test migrations locally before deploying to production
5. **Never Modify Applied Migrations**: Once a migration is applied, don't modify it - create a new one instead
6. **Backup Before Production**: Always backup your database before applying migrations in production
7. **Use Transactions**: Flask-Migrate runs migrations in transactions by default - keep this enabled

### Troubleshooting

#### Migration Fails with "No changes in schema detected"

This means your model changes don't require a schema change (e.g., you only modified a method, not a column). No migration is needed.

#### Migration Fails with "Database is locked"

Ensure no other processes are using the database. Stop your application and try again.

#### Need to Reset Database (Development Only)

In development, you can reset the database:

```bash
# Drop all tables
flask db downgrade base

# Reapply all migrations
flask db upgrade
```

**Warning**: This will delete all data. Never do this in production!

### Example: Complete Migration Workflow

Here's a complete example of adding a new field to the User model:

```bash
# 1. Modify the model
# Edit be/app/models/user.py and add: bio = db.Column(db.Text)

# 2. Generate migration
cd /dndbook/be
source venv/bin/activate
flask db migrate -m "Add bio field to users table"

# 3. Review the migration
cat migrations/versions/<latest_migration_file>.py

# 4. Apply the migration
flask db upgrade

# 5. Test the application
./run-standalone.sh

# 6. Commit the migration file
git add migrations/versions/<latest_migration_file>.py
git commit -m "feat(be) [feature/user-bio] Add bio field to users table"
```

---

## Adding a New Language

D&D Book uses vue-i18n for internationalization. Adding a new language involves three steps:

### Step 1: Create the Translation File

Create a new YAML file in `fe/src/locales/` with the language code (e.g., `pt.yaml` for Portuguese):

```bash
# Example: fe/src/locales/pt.yaml
app:
  title: "D&D Book"
  menu: "Menu"
  settings: "Configurações"
  language: "Idioma"
  theme: "Tema"

auth:
  login: "Entrar"
  register: "Registrar"
  logout: "Sair"
  username: "Nome de usuário"
  email: "Email"
  password: "Senha"
  # ... translate all other keys
```

**Important:** Copy the structure from an existing locale file (e.g., `en.yaml`) and translate all keys. The application will warn if any translation keys are missing.

### Step 2: Register the Language

Add the new language to `fe/src/config/locales.js`:

```javascript
export const LOCALE_NAMES = {
  en: 'English',
  it: 'Italiano',
  de: 'Deutsch',
  es: 'Español',
  fr: 'Français',
  pt: 'Português'  // Add this line
};
```

### Step 3: Configure Environment Variable

Add the new language code to the `VITE_AVAILABLE_LOCALES` environment variable in your `.env` file:

```bash
# In .env (root or fe/.env)
VITE_AVAILABLE_LOCALES=en,it,de,es,fr,pt
```

### Step 4: Test the Translation

1. Restart the frontend development server
2. Open the application in your browser
3. Go to Settings → Language
4. Select your new language
5. Verify all text is translated correctly

---

## Creating a New API Endpoint

This guide shows how to add a new API endpoint following the controller/service/models pattern.

### Example: Adding a "Notes" Feature

Let's say you want to add a notes feature where users can create notes for their campaigns.

#### Step 1: Create the Model

Create `be/app/models/note.py`:

```python
from datetime import datetime
from app import db


class Note(db.Model):
    """Note model for campaign notes."""
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    campaign = db.relationship('Campaign', backref=db.backref('notes', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('notes', lazy=True, cascade='all, delete-orphan'))

    def to_dict(self):
        """Convert note object to dictionary representation."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'campaign_id': self.campaign_id,
            'user_id': self.user_id
        }
```

Add the model to `be/app/models/__init__.py`:

```python
from app.models.note import Note

# Add to the __all__ list or import statement
```

#### Step 2: Create the Service

Create `be/app/services/notes_service.py`:

```python
from app import db
from app.models import Note, Campaign, User


class NotesService:
    """Service for handling note business logic."""

    @staticmethod
    def create_note(campaign_id, user_id, title, content):
        """
        Create a new note for a campaign.

        Args:
            campaign_id (int): ID of the campaign
            user_id (int): ID of the user creating the note
            title (str): Note title
            content (str): Note content

        Returns:
            Note: The created note

        Raises:
            ValueError: If campaign doesn't exist or user is not a member
        """
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            raise ValueError('Campaign not found')

        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')

        # Check if user is a member of the campaign
        if user not in campaign.members and campaign.owner_id != user_id:
            raise ValueError('User is not a member of this campaign')

        note = Note(
            title=title,
            content=content,
            campaign_id=campaign_id,
            user_id=user_id
        )

        db.session.add(note)
        db.session.commit()

        return note

    @staticmethod
    def get_campaign_notes(campaign_id, user_id):
        """
        Get all notes for a campaign.

        Args:
            campaign_id (int): ID of the campaign
            user_id (int): ID of the user requesting the notes

        Returns:
            list: List of note dictionaries

        Raises:
            ValueError: If campaign doesn't exist or user is not a member
        """
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            raise ValueError('Campaign not found')

        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')

        if user not in campaign.members and campaign.owner_id != user_id:
            raise ValueError('User is not a member of this campaign')

        notes = Note.query.filter_by(campaign_id=campaign_id).all()
        return [note.to_dict() for note in notes]

    @staticmethod
    def update_note(note_id, user_id, title=None, content=None):
        """
        Update an existing note.

        Args:
            note_id (int): ID of the note to update
            user_id (int): ID of the user updating the note
            title (str, optional): New title
            content (str, optional): New content

        Returns:
            Note: The updated note

        Raises:
            ValueError: If note doesn't exist or user is not the owner
        """
        note = Note.query.get(note_id)
        if not note:
            raise ValueError('Note not found')

        if note.user_id != user_id:
            raise ValueError('User is not the owner of this note')

        if title is not None:
            note.title = title
        if content is not None:
            note.content = content

        db.session.commit()

        return note

    @staticmethod
    def delete_note(note_id, user_id):
        """
        Delete a note.

        Args:
            note_id (int): ID of the note to delete
            user_id (int): ID of the user deleting the note

        Raises:
            ValueError: If note doesn't exist or user is not the owner
        """
        note = Note.query.get(note_id)
        if not note:
            raise ValueError('Note not found')

        if note.user_id != user_id:
            raise ValueError('User is not the owner of this note')

        db.session.delete(note)
        db.session.commit()
```

#### Step 3: Create the Controller

Create `be/app/controllers/notes_controller.py`:

```python
from flask import Blueprint, request, jsonify
from app.services.notes_service import NotesService
from app.jwt.jwt_utils import token_required

bp = Blueprint('notes', __name__, url_prefix='/api/notes')


@bp.route('/', methods=['POST'])
@token_required
def create_note(current_user):
    """
    Create a new note.

    Expected JSON payload:
        - campaign_id (int): ID of the campaign
        - title (str): Note title
        - content (str): Note content

    Returns:
        JSON response with:
        - 201: Success with note data
        - 400: Missing required fields or validation error
        - 401: Unauthorized
    """
    data = request.get_json()

    if not data or not data.get('campaign_id') or not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        note = NotesService.create_note(
            campaign_id=data['campaign_id'],
            user_id=current_user.id,
            title=data['title'],
            content=data['content']
        )
        return jsonify({
            'message': 'Note created successfully',
            'note': note.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/campaign/<int:campaign_id>', methods=['GET'])
@token_required
def get_campaign_notes(current_user, campaign_id):
    """
    Get all notes for a campaign.

    Returns:
        JSON response with:
        - 200: Success with notes data
        - 400: Validation error
        - 401: Unauthorized
    """
    try:
        notes = NotesService.get_campaign_notes(
            campaign_id=campaign_id,
            user_id=current_user.id
        )
        return jsonify({'notes': notes}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<int:note_id>', methods=['PUT'])
@token_required
def update_note(current_user, note_id):
    """
    Update an existing note.

    Expected JSON payload:
        - title (str, optional): New title
        - content (str, optional): New content

    Returns:
        JSON response with:
        - 200: Success with updated note data
        - 400: Validation error
        - 401: Unauthorized
    """
    data = request.get_json()

    try:
        note = NotesService.update_note(
            note_id=note_id,
            user_id=current_user.id,
            title=data.get('title'),
            content=data.get('content')
        )
        return jsonify({
            'message': 'Note updated successfully',
            'note': note.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<int:note_id>', methods=['DELETE'])
@token_required
def delete_note(current_user, note_id):
    """
    Delete a note.

    Returns:
        JSON response with:
        - 200: Success
        - 400: Validation error
        - 401: Unauthorized
    """
    try:
        NotesService.delete_note(
            note_id=note_id,
            user_id=current_user.id
        )
        return jsonify({'message': 'Note deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

#### Step 4: Register the Blueprint

Add the controller to `be/app/__init__.py`:

```python
# In the create_app() function, after other imports:
from app.controllers import notes_controller as notes

# Register the blueprint:
app.register_blueprint(notes.bp)
```

#### Step 5: Create Database Migration

If using Flask-Migrate, create a migration:

```bash
cd be
flask db migrate -m "Add notes table"
flask db upgrade
```

Alternatively, for development, you can manually add the table to `be/docker-entrypoint-initdb.d/init-db.sql`.

#### Step 6: Test the Endpoint

Use curl or Postman to test your new endpoint:

```bash
# Create a note
curl -X POST http://localhost:5000/api/notes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"campaign_id": 1, "title": "Meeting Notes", "content": "Discussed the dragon attack..."}'

# Get campaign notes
curl -X GET http://localhost:5000/api/notes/campaign/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Writing Tests

D&D Book uses pytest for testing. Tests follow the GIVEN-WHEN-THEN pattern for clarity.

### Test Structure

```
be/tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_auth.py             # Controller tests
└── services/                # Service layer tests
    ├── test_auth_service.py
    ├── test_campaigns_service.py
    └── ...
```

### Test Fixtures

The `conftest.py` file provides common fixtures:

```python
@pytest.fixture
def app():
    """Creates and configures a test application instance."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Provides a test client for the application."""
    return app.test_client()
```

### Writing Service Tests

Service tests should test business logic in isolation. Here's an example following the GIVEN-WHEN-THEN pattern:

```python
"""
Unit tests for NotesService using GIVEN-WHEN-THEN pattern.
"""
import pytest
from app.services.notes_service import NotesService
from app.models import Note, Campaign, User


def test_create_note_success(app):
    """GIVEN a valid campaign and user
    WHEN creating a note with valid data
    THEN the note should be created successfully
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        campaign = Campaign(name='Test Campaign', description='Test', owner_id=user.id)
        db.session.add(campaign)
        db.session.commit()
        
        # WHEN
        note = NotesService.create_note(
            campaign_id=campaign.id,
            user_id=user.id,
            title='Test Note',
            content='Test content'
        )
        
        # THEN
        assert note is not None
        assert note.title == 'Test Note'
        assert note.content == 'Test content'
        assert note.campaign_id == campaign.id
        assert note.user_id == user.id


def test_create_note_campaign_not_found(app):
    """GIVEN a non-existent campaign ID
    WHEN attempting to create a note
    THEN should raise ValueError with 'Campaign not found'
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='Campaign not found'):
            NotesService.create_note(
                campaign_id=999,
                user_id=user.id,
                title='Test Note',
                content='Test content'
            )


def test_create_note_user_not_member(app):
    """GIVEN a campaign and a non-member user
    WHEN attempting to create a note
    THEN should raise ValueError with 'User is not a member of this campaign'
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        non_member = User(username='nonmember', email='nonmember@example.com')
        non_member.set_password('password123')
        db.session.add(non_member)
        db.session.commit()
        
        campaign = Campaign(name='Test Campaign', description='Test', owner_id=owner.id)
        db.session.add(campaign)
        db.session.commit()
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='User is not a member of this campaign'):
            NotesService.create_note(
                campaign_id=campaign.id,
                user_id=non_member.id,
                title='Test Note',
                content='Test content'
            )
```

### Writing Controller Tests

Controller tests should test HTTP endpoints:

```python
"""
Unit tests for NotesController.
"""
import pytest
import json
from app.services.notes_service import NotesService
from app.models import User, Campaign


def test_create_note_endpoint(client, app):
    """GIVEN a logged-in user and valid campaign
    WHEN sending a POST request to create a note
    THEN should return 201 with note data
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        campaign = Campaign(name='Test Campaign', description='Test', owner_id=user.id)
        db.session.add(campaign)
        db.session.commit()
        
        # Login to get token
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        token = json.loads(response.data)['token']
        
        # WHEN
        response = client.post('/api/notes/', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'campaign_id': campaign.id,
                'title': 'Test Note',
                'content': 'Test content'
            }
        )
        
        # THEN
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['note']['title'] == 'Test Note'
        assert data['note']['content'] == 'Test content'
```

### Running Tests

Run all tests:
```bash
cd be
pytest
```

Run specific test file:
```bash
pytest tests/services/test_notes_service.py
```

Run with coverage:
```bash
pytest --cov=app tests/
```

Run with verbose output:
```bash
pytest -v
```

### Test Guidelines

- **Use GIVEN-WHEN-THEN pattern** for test clarity
- **Test one thing per test** - keep tests focused
- **Use descriptive test names** that explain what is being tested
- **Test both success and failure cases**
- **Use fixtures** for common setup (users, campaigns, etc.)
- **Avoid testing implementation details** - test behavior, not internals
- **Keep tests independent** - each test should be able to run alone

---

## Code Style Guidelines

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Maximum line length: 100 characters
- Use meaningful variable and function names

### JavaScript/Vue (Frontend)

- Use ES6+ syntax
- Follow Vue.js style guide
- Use composition API for new components
- Write JSDoc comments for complex functions
- Use meaningful variable and function names

### General

- Write clear, descriptive commit messages
- Keep functions small and focused
- Don't repeat yourself (DRY principle)
- Add comments for complex logic
- Remove unused code and imports

---

## Submitting Changes

1. **Fork the repository** on GitHub
2. **Create a feature branch** from the main branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the guidelines above
4. **Write tests** for your changes
5. **Run tests** to ensure everything passes:
   ```bash
   cd be && pytest
   cd fe && npm test
   ```
6. **Commit your changes** following our commit message standard:

   **Commit Message Format:**
   ```
   type(project_name) [branch] header

   body

   footer (optional)
   ```

   **Available commit types:**
   - `feat` - New feature
   - `fix` - Bug fix
   - `docs` - Documentation changes
   - `perf` - Performance improvements
   - `refactor` - Code refactoring
   - `test` - Test additions or changes
   - `build` - Build system changes
   - `chore` - Maintenance tasks

   **Example commit messages:**
   ```bash
   # For backend changes
   feat(be) [feature/notes] Add notes CRUD operations

   Implement create, read, update, and delete operations for campaign notes.
   Includes model, service, and controller layers with proper validation.

   Closes #123

   # For frontend changes
   fix(fe) [bugfix/language-selector] Fix language selector dropdown

   The dropdown was not closing after selection in Safari browser.
   Added proper event handling to ensure consistent behavior across browsers.

   # For documentation
   docs(root) [update-readme] Update installation instructions

   Clarified Docker setup steps and added troubleshooting section.
   ```
7. **Push to your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Open a Pull Request** on GitHub with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots for UI changes (if applicable)

### Pull Request Guidelines

- Keep PRs focused and small
- Ensure all tests pass
- Update documentation if needed
- Request review from maintainers
- Be responsive to feedback

---

## Getting Help

If you need help contributing:

- Check existing issues on GitHub
- Read the codebase for examples
- Ask questions in issues or discussions
- Review the User Manual for feature context

Thank you for contributing to D&D Book! 🎲
