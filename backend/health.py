from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
import logging
from models import db_instance
from utils import ai_service
from logger import get_logger, log_user_action

logger = get_logger('health')
health_bp = Blueprint('health', __name__)

@health_bp.route('/daily-entry', methods=['POST'])
@health_bp.route('/submit_daily_data', methods=['POST'])
@jwt_required()
def submit_daily_data():
    """Submit daily data endpoint"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['date', 'height', 'weight', 'breakfast', 'lunch', 'dinner']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Parse date
        entry_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        # Check if entry already exists for this date
        existing_entry = db_instance.get_daily_entry_by_date(user_id, entry_date)
        
        if existing_entry:
            return jsonify({'error': 'Entry already exists for this date'}), 409
        
        # Create daily entry
        entry_data = {
            'user_id': user_id,
            'date': entry_date,
            'height': float(data['height']),
            'weight': float(data['weight']),
            'breakfast': data['breakfast'],
            'lunch': data['lunch'],
            'dinner': data['dinner'],
            'created_at': datetime.now(timezone.utc)
        }
        
        doc_ref = db_instance.create_daily_entry(entry_data)
        
        log_user_action(user_id, 'DAILY_ENTRY_CREATED', f'Created entry for {entry_date}')
        
        return jsonify({
            'message': 'Daily data submitted successfully',
            'entry_id': doc_ref[1].id
        }), 201
        
    except Exception as e:
        logger.error(f"Daily data submission error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@health_bp.route('/daily-entries', methods=['GET'])
@health_bp.route('/get_daily_data', methods=['GET'])
@jwt_required()
def get_daily_data():
    """Get user's daily data endpoint"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        limit = int(request.args.get('limit', 30))
        
        # Fetch entries
        entries = db_instance.get_daily_entries(user_id, limit)
        
        entries_data = []
        for entry in entries:
            entry_dict = entry.to_dict()
            entry_dict['id'] = entry.id
            entry_dict['date'] = entry_dict['date'].isoformat() if entry_dict.get('date') else None
            entries_data.append(entry_dict)
        
        return jsonify({
            'message': 'Daily data retrieved successfully',
            'data': entries_data,
            'total_count': len(entries_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Get daily data error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@health_bp.route('/health-suggestion', methods=['GET'])
@health_bp.route('/get_daily_suggestion', methods=['POST'])
@jwt_required()
def get_daily_suggestion():
    """Get daily health suggestion from Gemini AI"""
    try:
        user_id = get_jwt_identity()
        
        # Check if AI service is available
        if not ai_service.is_available():
            return jsonify({'error': 'Health suggestions are currently unavailable'}), 503
        
        # Check if user already got suggestion today
        today = datetime.now(timezone.utc).date()
        # Convert date to datetime for Firestore compatibility
        today_datetime = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        
        existing_suggestion = db_instance.get_health_suggestion_by_date(user_id, today_datetime)
        
        if existing_suggestion:
            log_user_action(user_id, 'HEALTH_SUGGESTION_RETRIEVED', 'Retrieved existing daily suggestion')
            return jsonify({
                'message': 'Daily suggestion already received',
                'suggestion': existing_suggestion[0].to_dict()['suggestion'],
                'already_received': True
            }), 200
        
        # Get user's recent entries for context
        recent_entries = db_instance.get_daily_entries(user_id, 7)
        
        # Get user profile
        user_doc = db_instance.get_user_by_id(user_id)
        user_data = user_doc.to_dict()
        
        # Generate suggestion using AI
        suggestion = ai_service.generate_health_suggestion(user_data, recent_entries)
        
        # Store suggestion in database with datetime object
        suggestion_data = {
            'user_id': user_id,
            'date': today_datetime,  # Store as datetime object
            'suggestion': suggestion,
            'created_at': datetime.now(timezone.utc)
        }
        
        db_instance.create_health_suggestion(suggestion_data)
        
        log_user_action(user_id, 'HEALTH_SUGGESTION_GENERATED', 'Generated new daily health suggestion')
        
        return jsonify({
            'message': 'Daily suggestion generated successfully',
            'suggestion': suggestion,
            'already_received': False
        }), 200
        
    except Exception as e:
        logger.error(f"Health suggestion error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
