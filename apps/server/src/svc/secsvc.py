"""
Security Service Module
"""
from svc.envsvc import AppEnv


class SecSvc:
    """
    Singleton Security Service
    Centralized access to security-related configuration and utilities.
    """

    _instance = None
    _settings: AppEnv | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecSvc, cls).__new__(cls)
            cls._instance._init_settings()
        return cls._instance

    def _init_settings(self) -> None:
        """
        Initialize settings once per application lifecycle.
        """
        if self._settings is None:
            self._settings = AppEnv()

    def get_appenv(self) -> AppEnv:
        """
        Returns application environment configuration.
        """
        return self._settings
