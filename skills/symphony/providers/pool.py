# -*- coding: utf-8 -*-
"""
ProviderPool - Fixed version with auto-default DB path
Root cause fix: db_path now defaults to symphony.db
"""
import time
import json
import sqlite3
import os
from typing import Dict, List, Any, Optional
from loguru import logger

# Default DB path
DEFAULT_DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

class Provider:
    """Provider wrapper"""
    
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.enabled = config.get("enabled", True)
        self.load = 0
        self.last_used = 0
        self.total_requests = 0
    
    def is_available(self) -> bool:
        return self.enabled
    
    def get_priority(self) -> float:
        return self.load + (time.time() - self.last_used) / 3600.0

class ProviderPool:
    """Model provider pool - FIXED default path"""
    
    def __init__(self, db_path: Optional[str] = None):
        # FIX: Use default path if None
        self.db_path = db_path if db_path else DEFAULT_DB_PATH
        self.providers: Dict[str, Provider] = {}
        self._load_providers()
        logger.info(f"ProviderPool initialized, {len(self.providers)} providers")
    
    def _load_providers(self):
        """Load providers from database"""
        if not self.db_path or not os.path.exists(self.db_path):
            logger.error(f"Database not found: {self.db_path}")
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        try:
            from db.database import SymphonyDatabase
            db = SymphonyDatabase(self.db_path)
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT provider_code, provider_name, base_url, api_key FROM provider_registry WHERE is_enabled = 1")
            
            for row in cursor.fetchall():
                code, name, base_url, api_key = row
                config = {
                    "name": name,
                    "base_url": base_url,
                    "api_key": api_key,
                    "enabled": True
                }
                provider = Provider(code, config)
                self.providers[code] = provider
                logger.debug(f"Registered provider: {name}")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to load providers: {e}")
    
    def register_provider(self, code: str, provider: Provider):
        self.providers[code] = provider
    
    def unregister_provider(self, code: str):
        if code in self.providers:
            del self.providers[code]
    
    def select_provider(self) -> Optional[Provider]:
        """Select best available provider"""
        available = [p for p in self.providers.values() if p.is_available()]
        if not available:
            return None
        return min(available, key=lambda p: p.get_priority())
    
    def release_provider(self, code: str):
        if code in self.providers:
            self.providers[code].load = max(0, self.providers[code].load - 1)
    
    def get_online_models(self) -> List[Dict]:
        """Get list of online models from all providers"""
        models = []
        for code, provider in self.providers.items():
            if provider.is_available():
                models.append({"provider": code, "name": provider.name})
        return models
    
    def get_stats(self) -> Dict:
        """Get provider statistics"""
        return {
            "total_providers": len(self.providers),
            "online_providers": len([p for p in self.providers.values() if p.is_available()]),
            "db_path": self.db_path
        }
