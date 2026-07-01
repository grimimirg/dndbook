"""Unit tests for NotesService using GIVEN-WHEN-THEN pattern."""

import pytest
from app import db
from app.services.notes_service import NotesService
from app.models import Campaign, User, Note


def test_create_note_as_owner(app):
    with app.app_context():
        owner = User(username="owner", email="owner@example.com")
        owner.set_password("password123")
        db.session.add(owner)
        db.session.commit()

        campaign = Campaign(
            name="Test Campaign",
            description="Test description",
            owner_id=owner.id,
            character_creation_mode="optional",
        )
        db.session.add(campaign)
        db.session.commit()

        note = NotesService.create_note(
            user=owner,
            campaign_id=campaign.id,
            title="DM Secret",
            content="Hidden details",
            visibility="personal",
        )

        assert note is not None
        assert note.title == "DM Secret"
        assert note.visibility == "personal"
        assert note.owner_id == owner.id


def test_create_note_unauthorized(app):
    with app.app_context():
        owner = User(username="owner", email="owner@example.com")
        owner.set_password("password123")
        db.session.add(owner)
        other = User(username="player", email="player@example.com")
        other.set_password("password123")
        db.session.add(other)
        db.session.commit()

        campaign = Campaign(name="Test", owner_id=owner.id, character_creation_mode="optional")
        db.session.add(campaign)
        db.session.commit()

        with pytest.raises(ValueError, match="Unauthorized"):
            NotesService.create_note(user=other, campaign_id=campaign.id, title="X")


def test_create_note_invalid_visibility(app):
    with app.app_context():
        owner = User(username="owner", email="owner@example.com")
        owner.set_password("password123")
        db.session.add(owner)
        db.session.commit()

        campaign = Campaign(name="Test", owner_id=owner.id, character_creation_mode="optional")
        db.session.add(campaign)
        db.session.commit()

        with pytest.raises(ValueError, match="visibility must be"):
            NotesService.create_note(user=owner, campaign_id=campaign.id, title="X", visibility="public")


def test_get_notes_dm_sees_all(app):
    with app.app_context():
        owner = User(username="owner", email="owner@example.com")
        owner.set_password("password123")
        db.session.add(owner)
        db.session.commit()

        campaign = Campaign(name="Test", owner_id=owner.id, character_creation_mode="optional")
        db.session.add(campaign)
        db.session.commit()

        NotesService.create_note(owner, campaign.id, "Personal", visibility="personal")
        NotesService.create_note(owner, campaign.id, "Player", visibility="players")

        notes = NotesService.get_notes(campaign.id, owner)
        assert len(notes) == 2


def test_get_notes_player_permitted(app):
    with app.app_context():
        owner = User(username="owner", email="owner@example.com")
        owner.set_password("password123")
        db.session.add(owner)
        player = User(username="player", email="player@example.com")
        player.set_password("password123")
        db.session.add(player)
        db.session.commit()

        campaign = Campaign(name="Test", owner_id=owner.id, character_creation_mode="optional")
        db.session.add(campaign)
        campaign.members.append(player)
        db.session.commit()

        pnote = NotesService.create_note(owner, campaign.id, "For Players", visibility="players")
        NotesService.create_note(owner, campaign.id, "DM Secret", visibility="personal")
        NotesService.set_note_permissions(pnote.id, owner, [player.id])

        notes = NotesService.get_notes(campaign.id, player)
        assert len(notes) == 1
        assert notes[0]["title"] == "For Players"


def test_get_note_unauthorized(app):
    with app.app_context():
        owner = User(username="owner", email="owner@example.com")
        owner.set_password("password123")
        db.session.add(owner)
        other = User(username="other", email="other@example.com")
        other.set_password("password123")
        db.session.add(other)
        db.session.commit()

        campaign = Campaign(name="Test", owner_id=owner.id, character_creation_mode="optional")
        db.session.add(campaign)
        db.session.commit()

        note = NotesService.create_note(owner, campaign.id, "Secret", visibility="personal")
        with pytest.raises(ValueError, match="Unauthorized"):
            NotesService.get_note(note.id, other)


def test_update_note(app):
    with app.app_context():
        owner = User(username="owner", email="owner@example.com")
        owner.set_password("password123")
        db.session.add(owner)
        db.session.commit()

        campaign = Campaign(name="Test", owner_id=owner.id, character_creation_mode="optional")
        db.session.add(campaign)
        db.session.commit()

        note = NotesService.create_note(owner, campaign.id, "Original")
        updated = NotesService.update_note(note.id, owner, title="Updated", content="New content")

        assert updated.title == "Updated"
        assert updated.content == "New content"


def test_delete_note(app):
    with app.app_context():
        owner = User(username="owner", email="owner@example.com")
        owner.set_password("password123")
        db.session.add(owner)
        db.session.commit()

        campaign = Campaign(name="Test", owner_id=owner.id, character_creation_mode="optional")
        db.session.add(campaign)
        db.session.commit()

        note = NotesService.create_note(owner, campaign.id, "To Delete")
        NotesService.delete_note(note.id, owner)
        assert Note.query.get(note.id) is None


def test_to_dict_no_permissions_for_players(app):
    with app.app_context():
        owner = User(username="owner", email="owner@example.com")
        owner.set_password("password123")
        db.session.add(owner)
        player = User(username="player", email="player@example.com")
        player.set_password("password123")
        db.session.add(player)
        db.session.commit()

        campaign = Campaign(name="Test", owner_id=owner.id, character_creation_mode="optional")
        db.session.add(campaign)
        campaign.members.append(player)
        db.session.commit()

        pnote = NotesService.create_note(owner, campaign.id, "Player", visibility="players")
        NotesService.set_note_permissions(pnote.id, owner, [player.id])

        pd = pnote.to_dict(user=player)
        assert "permitted_user_ids" not in pd

        od = pnote.to_dict(user=owner)
        assert "permitted_user_ids" in od
