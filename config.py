"""
Configuration Management
Handles environment variables and .env file loading
"""

import os
import logging
from typing import Dict, Any


# Default configuration
DEFAULT_CONFIG = {
    # Email Configuration
    "EMAIL_FROM": "",
    "EMAIL_PASSWORD": "",
    "EMAIL_TO": "",
    "SMTP_SERVER": "smtp.gmail.com",
    "SMTP_PORT": 587,
    
    # Gemini AI Configuration
    "GEMINI_API_KEY": "",
    "GEMINI_MODEL": "gemini-2.0-flash",
    
    # System Thresholds
    "CONFIDENCE_THRESHOLD": 0.8,
    "MAX_RETRIES": 3,
    
    # Logging Configuration
    "LOG_LEVEL": "INFO",
    "LOG_FILE": "logs/incident_response.log"
}

logger = logging.getLogger("config")


class ConfigManager:
    """Singleton configuration manager"""
    
    _instance = None
    _config = {}
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self.__class__._initialized:
            self._load_config()
            self.__class__._initialized = True
    
    def _load_config(self):
        """Load configuration from environment variables and .env file"""
        config = DEFAULT_CONFIG.copy()
        
        # Override with environment variables
        for key in config:
            env_value = os.environ.get(key)
            if env_value is not None:
                if isinstance(config[key], (int, float)):
                    try:
                        if isinstance(config[key], int):
                            config[key] = int(env_value)
                        else:
                            config[key] = float(env_value)
                    except ValueError:
                        logger.warning(f"Invalid numeric value for {key}: {env_value}")
                else:
                    config[key] = env_value
        
        # Load from .env file if exists
        self._load_env_file(config)
        self._config = config
    
    def _load_env_file(self, config: Dict[str, Any]) -> None:
        """Load configuration from .env file"""
        env_file = os.environ.get("ENV_FILE", ".env")
        if os.path.exists(env_file):
            try:
                with open(env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                key = key.strip()
                                value = value.strip()
                                
                                # Remove quotes
                                if (value.startswith('"') and value.endswith('"')) or \
                                   (value.startswith("'") and value.endswith("'")):
                                    value = value[1:-1]
                                
                                if key in config:
                                    if isinstance(config[key], (int, float)):
                                        try:
                                            if isinstance(config[key], int):
                                                config[key] = int(value)
                                            else:
                                                config[key] = float(value)
                                        except ValueError:
                                            logger.warning(f"Invalid numeric value for {key}: {value}")
                                    else:
                                        config[key] = value
            except Exception as e:
                logger.warning(f"Error loading .env file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def validate(self) -> None:
        """Validate required configuration values"""
        required_keys = ["GEMINI_API_KEY", "EMAIL_FROM", "EMAIL_PASSWORD", "EMAIL_TO"]
        missing = [key for key in required_keys if not self._config.get(key)]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()


# Convenience functions
def get_config() -> ConfigManager:
    """Get config manager instance"""
    return ConfigManager()


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a specific config value"""
    return get_config().get(key, default)


def validate_config() -> None:
    """Validate configuration"""
    get_config().validate()
