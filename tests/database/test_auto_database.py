import unittest
from pathlib import Path

from pjtools.configurator import AutoConfigurator
from pjtools.database import AutoDatabase
from pjtools.database.base import BaseDatabase
from pjtools.database.sqlite_wrapper import SQLiteDatabase


class TestAutoDatabase(unittest.TestCase):

    def setUp(self):
        sqllite_cfg_path = 'tests/data/dummy_sqlite_config.py'
        self.sqlite_db_cfg = AutoConfigurator.fromfile(sqllite_cfg_path)
        self.sqlite_db_cfg = self.sqlite_db_cfg.to_dict()['database']
        unknown_db_cfg_path = 'tests/data/dummy_unknowndb_config.py'
        self.unknown_db_cfg = AutoConfigurator.fromfile(unknown_db_cfg_path)
        self.unknown_db_cfg = self.unknown_db_cfg.to_dict()['database']

    def test_from_config_sqlite(self):
        db = AutoDatabase.from_config(self.sqlite_db_cfg)

        self.assertIsInstance(db, BaseDatabase)
        self.assertIsInstance(db, SQLiteDatabase)

    def test_from_config_unsupported_db(self):
        with self.assertRaises(ValueError):
            AutoDatabase.from_config(self.unknown_db_cfg)
