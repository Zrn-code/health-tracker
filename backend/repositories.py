from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
import firebase_admin
from firebase_admin import credentials, firestore
from exceptions import DatabaseError, NotFoundError
import logging

logger = logging.getLogger(__name__)

class BaseRepository(ABC):
    """Base repository interface"""
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> str:
        """Create a new record"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID"""
        pass
    
    @abstractmethod
    def update(self, id: str, data: Dict[str, Any]) -> bool:
        """Update record"""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete record"""
        pass

class FirestoreRepository(BaseRepository):
    """Base Firestore repository"""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.db = None
        self._initialize_firestore()
    
    def _initialize_firestore(self):
        """Initialize Firestore client"""
        try:
            if not firebase_admin._apps:
                from config import get_config
                config = get_config()
                cred = credentials.Certificate(config.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            logger.info(f"Firestore initialized for collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Firestore initialization error: {e}")
            raise DatabaseError(f"Database initialization failed: {str(e)}")
    
    def create(self, data: Dict[str, Any]) -> str:
        """Create a new document"""
        try:
            doc_ref = self.db.collection(self.collection_name).add(data)
            return doc_ref[1].id
        except Exception as e:
            logger.error(f"Create operation failed: {e}")
            raise DatabaseError(f"Failed to create record: {str(e)}")
    
    def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        try:
            doc = self.db.collection(self.collection_name).document(id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                logger.debug(f"Retrieved document {id}: {data}")
                return data
            else:
                logger.warning(f"Document {id} not found in collection {self.collection_name}")
            return None
        except Exception as e:
            logger.error(f"Get by ID operation failed: {e}")
            raise DatabaseError(f"Failed to retrieve record: {str(e)}")
    
    def update(self, id: str, data: Dict[str, Any]) -> bool:
        """Update document"""
        try:
            self.db.collection(self.collection_name).document(id).update(data)
            return True
        except Exception as e:
            logger.error(f"Update operation failed: {e}")
            raise DatabaseError(f"Failed to update record: {str(e)}")
    
    def delete(self, id: str) -> bool:
        """Delete document"""
        try:
            self.db.collection(self.collection_name).document(id).delete()
            return True
        except Exception as e:
            logger.error(f"Delete operation failed: {e}")
            raise DatabaseError(f"Failed to delete record: {str(e)}")

class UserRepository(FirestoreRepository):
    """User repository with specific user operations"""
    
    def __init__(self):
        super().__init__('users')
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            docs = self.db.collection(self.collection_name).where(
                filter=firestore.FieldFilter('email', '==', email)
            ).get()
            
            if docs:
                doc = docs[0]
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            logger.error(f"Get by email operation failed: {e}")
            raise DatabaseError(f"Failed to retrieve user by email: {str(e)}")
    
    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            docs = self.db.collection(self.collection_name).where(
                filter=firestore.FieldFilter('username', '==', username)
            ).get()
            
            if docs:
                doc = docs[0]
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            logger.error(f"Get by username operation failed: {e}")
            raise DatabaseError(f"Failed to retrieve user by username: {str(e)}")
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return self.get_by_email(email) is not None
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        return self.get_by_username(username) is not None

class DailyEntryRepository(FirestoreRepository):
    """Daily entry repository"""
    
    def __init__(self):
        super().__init__('daily_entries')
    
    def get_by_user_and_date(self, user_id: str, entry_date: date) -> Optional[Dict[str, Any]]:
        """Get daily entry by user ID and date"""
        try:
            # Convert date to datetime for Firestore compatibility
            if isinstance(entry_date, date) and not isinstance(entry_date, datetime):
                entry_datetime = datetime.combine(entry_date, datetime.min.time())
            else:
                entry_datetime = entry_date
            
            docs = self.db.collection(self.collection_name).where(
                filter=firestore.FieldFilter('user_id', '==', user_id)
            ).where(
                filter=firestore.FieldFilter('date', '==', entry_datetime)
            ).get()
            
            if docs:
                doc = docs[0]
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            logger.error(f"Get by user and date operation failed: {e}")
            raise DatabaseError(f"Failed to retrieve daily entry: {str(e)}")
    
    def get_by_user(self, user_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        """Get user's daily entries"""
        try:
            docs = self.db.collection(self.collection_name).where(
                filter=firestore.FieldFilter('user_id', '==', user_id)
            ).order_by('date', direction=firestore.Query.DESCENDING).limit(limit).get()
            
            entries = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                entries.append(data)
            
            return entries
        except Exception as e:
            logger.error(f"Get user entries operation failed: {e}")
            raise DatabaseError(f"Failed to retrieve user entries: {str(e)}")
    
    def delete_by_user(self, user_id: str) -> int:
        """Delete all entries for a user"""
        try:
            docs = self.db.collection(self.collection_name).where(
                filter=firestore.FieldFilter('user_id', '==', user_id)
            ).get()
            
            count = 0
            for doc in docs:
                doc.reference.delete()
                count += 1
            
            return count
        except Exception as e:
            logger.error(f"Delete user entries operation failed: {e}")
            raise DatabaseError(f"Failed to delete user entries: {str(e)}")

class HealthSuggestionRepository(FirestoreRepository):
    """Health suggestion repository"""
    
    def __init__(self):
        super().__init__('health_suggestions')
    
    def get_by_user_and_date(self, user_id: str, suggestion_date: date) -> Optional[Dict[str, Any]]:
        """Get health suggestion by user ID and date"""
        try:
            if isinstance(suggestion_date, date) and not isinstance(suggestion_date, datetime):
                suggestion_datetime = datetime.combine(suggestion_date, datetime.min.time())
            else:
                suggestion_datetime = suggestion_date
            
            docs = self.db.collection(self.collection_name).where(
                filter=firestore.FieldFilter('user_id', '==', user_id)
            ).where(
                filter=firestore.FieldFilter('date', '==', suggestion_datetime)
            ).get()
            
            if docs:
                doc = docs[0]
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            logger.error(f"Get suggestion by user and date operation failed: {e}")
            raise DatabaseError(f"Failed to retrieve health suggestion: {str(e)}")
    
    def delete_by_user(self, user_id: str) -> int:
        """Delete all suggestions for a user"""
        try:
            docs = self.db.collection(self.collection_name).where(
                filter=firestore.FieldFilter('user_id', '==', user_id)
            ).get()
            
            count = 0
            for doc in docs:
                doc.reference.delete()
                count += 1
            
            return count
        except Exception as e:
            logger.error(f"Delete user suggestions operation failed: {e}")
            raise DatabaseError(f"Failed to delete user suggestions: {str(e)}")

# Repository instances
user_repo = UserRepository()
daily_entry_repo = DailyEntryRepository()
health_suggestion_repo = HealthSuggestionRepository()
