from typing import Dict

from .base import BaseDatabase
from .sqlite_wrapper import SQLiteDatabase


class AutoDatabase:
    """
    Automatically select the appropriate database class based on the
    configuration.
    """

    DATABASE_REGISTRY = {
        'sqlite': SQLiteDatabase,
    }

    @classmethod
    def from_config(cls, db_cfg: Dict) -> 'BaseDatabase':
        """
        Determine which database class to use based on the configuration
        and initialize it.

        Args:
            db_cfg (Dict): A dictionary containing database configuration
                parameters.

        Returns:
            BaseDatabase: An instance of the appropriate database class
                initialized with data from the configuration.
        """
        db_type = db_cfg.get('type')

        database_class = cls.DATABASE_REGISTRY.get(db_type)

        if database_class is None:
            raise ValueError(f"Unsupported database type '{db_type}'")

        return database_class(db_cfg)
