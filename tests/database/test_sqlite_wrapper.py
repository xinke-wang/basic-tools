import sqlite3
import unittest
from unittest.mock import MagicMock

from pjtools.configurator import AutoConfigurator
from pjtools.database.sqlite_wrapper import SQLiteDatabase


class TestSQLiteDatabase(unittest.TestCase):

    def setUp(self):
        cfg_path = 'tests/data/dummy_sqlite_config.py'
        self.db_cfg = AutoConfigurator.fromfile(cfg_path).to_dict()['database']

    def test_init(self):
        db = SQLiteDatabase(self.db_cfg)
        self.assertIsNotNone(db.connection)

    def test_connect(self):
        db = SQLiteDatabase(self.db_cfg)
        db.close()
        db.connect()
        self.assertIsNotNone(db.connection)

    def test_close(self):
        db = SQLiteDatabase(self.db_cfg)
        db.close()
        self.assertIsNone(db.connection)

    def test_create_table(self):
        db = SQLiteDatabase(self.db_cfg)
        schema = {'name': str, 'age': 'INTEGER', 'height': float}
        db.create_table('people', schema)

        cursor = db.connection.cursor()
        cursor.execute('PRAGMA table_info(people)')
        result = cursor.fetchall()
        result_as_tuples = [tuple(row) for row in result]

        expected_schema = [
            (0, 'name', 'TEXT', 0, None, 0),
            (1, 'age', 'INTEGER', 0, None, 0),
            (2, 'height', 'REAL', 0, None, 0),
        ]

        self.assertEqual(result_as_tuples, expected_schema)
        db.close()

    def test_drop_table(self):
        db = SQLiteDatabase(self.db_cfg)

        schema = {'name': 'TEXT', 'age': 'INTEGER'}
        db.create_table('test_table', schema)

        db.drop_table('test_table')

        cursor = db.connection.cursor()
        with self.assertRaises(sqlite3.OperationalError) as context:
            cursor.execute('SELECT * FROM test_table')

        self.assertTrue('no such table' in str(context.exception).lower())

        db.close()

    def test_insert(self):
        db = SQLiteDatabase(self.db_cfg)
        db.connect()
        db.connection.execute(
            'CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)'
        )

        test_data = {'name': 'Alice', 'age': 25}
        db.insert('test', test_data)
        cursor = db.connection.execute(
            "SELECT * FROM test WHERE name = 'Alice'")
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[1], 'Alice')
        self.assertEqual(row[2], 25)

        db.connection.execute('DROP TABLE test')
        db.close()

    def test_inserts(self):
        db = SQLiteDatabase(self.db_cfg)
        db.connect()

        db.connection.execute(
            'CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)'
        )
        test_data = [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}]
        db.inserts('test', test_data)

        cursor = db.connection.execute('SELECT * FROM test ORDER BY id ASC')
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][1], 'Alice')
        self.assertEqual(rows[0][2], 25)
        self.assertEqual(rows[1][1], 'Bob')
        self.assertEqual(rows[1][2], 30)
        db.connection.execute('DROP TABLE test')
        db.close()

    def test_delete(self):
        db = SQLiteDatabase(self.db_cfg)
        db.connect()

        db.connection.execute(
            'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)'
        )
        db.connection.execute(
            "INSERT INTO users (name, age) VALUES ('Alice', 25)")
        db.connection.commit()

        db.delete('users', {'name': 'Alice'})

        cursor = db.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE name='Alice'")
        self.assertIsNone(cursor.fetchone())

        db.connection.execute('DROP TABLE IF EXISTS users')
        db.connection.commit()
        db.close()

    def test_deletes(self):
        db = SQLiteDatabase(self.db_cfg)
        db.connect()

        db.connection.execute(
            'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)'
        )
        db.connection.execute(
            "INSERT INTO users (name, age) VALUES ('Alice', 25), ('Bob', 30)")
        db.connection.commit()

        db.deletes('users', [{'name': 'Alice'}, {'name': 'Bob'}])

        cursor = db.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE name='Alice' OR name='Bob'")
        self.assertIsNone(cursor.fetchone())

        db.connection.execute('DROP TABLE IF EXISTS users')
        db.connection.commit()
        db.close()

    def test_select(self):
        db = SQLiteDatabase(self.db_cfg)
        db.connect()
        db.connection.execute(
            'CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)'
        )

        test_data = {'name': 'Alice', 'age': 25}
        db.insert('test', test_data)

        data = db.select('test', {'name': 'Alice'})
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Alice')
        self.assertEqual(data[0]['age'], 25)

        db.connection.execute('DROP TABLE test')
        db.close()

    def test_selects(self):
        db = SQLiteDatabase(self.db_cfg)
        db.connect()

        db.connection.execute(
            'CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)'
        )
        test_data = [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}]
        db.inserts('test', test_data)

        data = db.selects('test', [{'name': 'Alice'}, {'age': 30}])
        self.assertEqual(len(data), 2)

        self.assertEqual(len(data[0]), 1)
        self.assertEqual(data[0][0]['name'], 'Alice')
        self.assertEqual(data[0][0]['age'], 25)

        self.assertEqual(len(data[1]), 1)
        self.assertEqual(data[1][0]['name'], 'Bob')
        self.assertEqual(data[1][0]['age'], 30)

        db.connection.execute('DROP TABLE test')
        db.close()

    def test_update(self):
        db = SQLiteDatabase(self.db_cfg)
        db.connect()
        db.connection.execute(
            'CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)'
        )

        test_data = {'name': 'Alice', 'age': 25}
        db.insert('test', test_data)

        update_data = {'name': 'Alice Updated'}
        db.update('test', update_data, {'name': 'Alice'})

        data = db.select('test', {'name': 'Alice Updated'})
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Alice Updated')
        self.assertEqual(data[0]['age'], 25)

        db.connection.execute('DROP TABLE test')
        db.close()

    def test_updates(self):
        db = SQLiteDatabase(self.db_cfg)
        db.connect()
        db.connection.execute(
            'CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)'
        )

        test_data = [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}]
        db.inserts('test', test_data)

        update_data = [{'name': 'Alice Updated'}, {'name': 'Bob Updated'}]
        conditions = [{'name': 'Alice'}, {'name': 'Bob'}]
        db.updates('test', update_data, conditions)

        data = db.selects('test', [{
            'name': 'Alice Updated'
        }, {
            'name': 'Bob Updated'
        }])
        self.assertEqual(len(data), 2)

        self.assertEqual(len(data[0]), 1)
        self.assertEqual(data[0][0]['name'], 'Alice Updated')
        self.assertEqual(data[0][0]['age'], 25)

        self.assertEqual(len(data[1]), 1)
        self.assertEqual(data[1][0]['name'], 'Bob Updated')
        self.assertEqual(data[1][0]['age'], 30)

        db.connection.execute('DROP TABLE test')
        db.close()

    def test_print_row(self):
        db = SQLiteDatabase(self.db_cfg)
        db.connect()

        db.create_table('test_table', {'name': str, 'age': int})
        db.insert('test_table', {'name': 'Alice', 'age': 25})
        db.print_row = MagicMock()
        db.print_row('test_table', {'name': 'Alice'})
        db.print_row.assert_called_once()

        db.close()

    def test_print_rows(self):
        db = SQLiteDatabase(self.db_cfg)
        db.connect()

        db.create_table('test_table', {'name': str, 'age': int})
        db.insert('test_table', {'name': 'Alice', 'age': 25})
        db.print_rows = MagicMock()
        db.print_rows('test_table', [{'name': 'Alice'}, {'age': 25}])
        db.print_rows.assert_called_once()

        db.close()

    def test_print_tables(self):
        db = SQLiteDatabase(self.db_cfg)
        db.connect()

        db.create_table('test_table', {'name': str, 'age': int})
        db.print_tables = MagicMock()
        db.print_tables()
        db.print_tables.assert_called_once()

        db.close()
