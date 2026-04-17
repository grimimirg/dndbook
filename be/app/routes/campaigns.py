from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Campaign
from app.auth import token_required
from app.mock_data import get_mock_campaigns, get_mock_campaign

bp = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')

@bp.route('', methods=['GET'])
@token_required
def get_campaigns(current_user):
    if current_app.config['MOCK_DATA']:
        user_id = current_user if isinstance(current_user, int) else current_user.id
        campaigns = get_mock_campaigns(user_id)
        return jsonify(campaigns), 200
    
    campaigns = Campaign.query.filter_by(owner_id=current_user.id).all()
    return jsonify([campaign.to_dict() for campaign in campaigns]), 200

@bp.route('', methods=['POST'])
@token_required
def create_campaign(current_user):
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Campaign name is required'}), 400
    
    campaign = Campaign(
        name=data['name'],
        description=data.get('description', ''),
        owner_id=current_user.id
    )
    
    db.session.add(campaign)
    db.session.commit()
    
    return jsonify(campaign.to_dict()), 201

@bp.route('/<int:campaign_id>', methods=['GET'])
@token_required
def get_campaign(current_user, campaign_id):
    if current_app.config['MOCK_DATA']:
        user_id = current_user if isinstance(current_user, int) else current_user.id
        campaign = get_mock_campaign(campaign_id)
        
        if not campaign or campaign['owner_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify(campaign), 200
    
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(campaign.to_dict()), 200

@bp.route('/<int:campaign_id>', methods=['PUT'])
@token_required
def update_campaign(current_user, campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if data.get('name'):
        campaign.name = data['name']
    if 'description' in data:
        campaign.description = data['description']
    
    db.session.commit()
    
    return jsonify(campaign.to_dict()), 200

@bp.route('/<int:campaign_id>', methods=['DELETE'])
@token_required
def delete_campaign(current_user, campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(campaign)
    db.session.commit()
    
    return jsonify({'message': 'Campaign deleted successfully'}), 200
