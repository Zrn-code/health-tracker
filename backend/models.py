import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
import logging
from config import Config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Firebase initialization error: {e}")
            raise e
    
    def get_user_by_email(self, email):
        """Get user by email"""
        users_ref = self.db.collection('users')
        return users_ref.where(filter=firestore.FieldFilter('email', '==', email)).get()
    
    def get_user_by_username(self, username):
        """Get user by username"""
        users_ref = self.db.collection('users')
        return users_ref.where(filter=firestore.FieldFilter('username', '==', username)).get()
    
    def create_user(self, user_data):
        """Create new user"""
        users_ref = self.db.collection('users')
        return users_ref.add(user_data)
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self.db.collection('users').document(user_id).get()
    
    def update_user(self, user_id, data):
        """Update user data"""
        return self.db.collection('users').document(user_id).update(data)
    
    def get_daily_entry_by_date(self, user_id, date):
        """Get daily entry by user ID and date"""
        return self.db.collection('daily_entries').where(
            filter=firestore.FieldFilter('user_id', '==', user_id)
        ).where(
            filter=firestore.FieldFilter('date', '==', date)
        ).get()
    
    def create_daily_entry(self, entry_data):
        """Create daily entry"""
        return self.db.collection('daily_entries').add(entry_data)
    
    def get_daily_entries(self, user_id, limit=30):
        """Get user's daily entries"""
        entries_ref = self.db.collection('daily_entries').where(
            filter=firestore.FieldFilter('user_id', '==', user_id)
        ).order_by('date', direction=firestore.Query.DESCENDING).limit(limit)
        return entries_ref.get()
    
    def get_health_suggestion_by_date(self, user_id, date):
        """Get health suggestion by user ID and date"""
        # Ensure date is a datetime object for Firestore
        if hasattr(date, 'date') and callable(date.date):
            # It's already a datetime object
            search_date = date
        else:
            # Convert date to datetime if needed
            search_date = datetime.combine(date, datetime.min.time()).replace(tzinfo=timezone.utc)
            
        return self.db.collection('health_suggestions').where(
            filter=firestore.FieldFilter('user_id', '==', user_id)
        ).where(
            filter=firestore.FieldFilter('date', '==', search_date)
        ).get()
    
    def create_health_suggestion(self, suggestion_data):
        """Create health suggestion"""
        return self.db.collection('health_suggestions').add(suggestion_data)

# Global database instance
db_instance = Database()
