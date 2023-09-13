import os
import os.path as osp
import sqlite3
from typing import Any, Dict, List, Tuple, Union

from .base import BaseDatabase


class SQLiteDatabase(BaseDatabase):
    """A wrapper class for SQLite databases."""

    PYTHON_SQLITE_TYPE_MAP = {
        int: 'INTEGER',
        float: 'REAL',
        str: 'TEXT',
        bytes: 'BLOB',
    }

    SQLITE_VALID_TYPES = {'INTEGER', 'REAL', 'TEXT', 'BLOB', 'NULL'}

    def __init__(self, db_cfg: Dict) -> None:
        """
        Initialize the database with the given file path and timeout.

        Args:
            db_cfg: A dictionary containing database configuration parameters.
        """
        self.db_path = db_cfg['path']
        if not osp.exists(osp.dirname(self.db_path)):
            os.makedirs(osp.dirname(self.db_path))
        self.timeout = db_cfg['timeout']
        self.connection = None
        self.connect()

    def connect(self) -> None:
        """Establish a connection to the database."""
        try:
            self.connection = sqlite3.connect(self.db_path,
                                              timeout=self.timeout)
            self.connection.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            print(f'An error occurred while connecting to the database: {e}')

    def close(self) -> None:
        """Close the connection to the database."""
        if self.connection:
            try:
                self.connection.close()
            except sqlite3.Error as e:
                print('An error occurred while closing the database '
                      f'connection: {e}')
            finally:
                self.connection = None

    def commit(self) -> None:
        """Commit the current transaction."""
        if self.connection:
            try:
                self.connection.commit()
            except sqlite3.Error as e:
                print(
                    f'An error occurred while committing the transaction: {e}')

    def execute(self,
                query: str,
                params: Tuple[Any, ...] = (),
                execute_many: bool = False) -> sqlite3.Cursor:
        """
        Execute a SQL query with the optional parameters.

        Args:
            query (str): The SQL query to execute.
            params (Tuple[Any, ...]): A tuple of parameters to use with the
                query.
            execute_many (bool): Whether to use the `executemany()` method
                instead

        Returns:
            sqlite3.Cursor: A cursor object.

        Examples:
            >>> db = SQLiteDatabase({'path': 'path/to/database.db',
                                     'timeout': 5})
            >>> db.execute("INSERT INTO users (name, age) VALUES (?, ?)",
                           ("Alice", 30))
        """
        try:
            cursor = self.connection.cursor()
            if not execute_many:
                cursor.execute(query, params)
            else:
                cursor.executemany(query, params)
            self.commit()
            return cursor
        except sqlite3.Error as e:
            print(f'An error occurred while executing the query: {e}')
            self.rollback()

    def create_table(
        self, table_name: str,
        schema: Dict[str, Union[type, str, Tuple[type,
                                                 str]]]) -> sqlite3.Cursor:
        """
        Create a new table with the specified schema.

        Args:
            table_name (str): The name of the table to be created.
            schema (Dict[str, Union[type, str, Tuple[type, str]]): A
                dictionary where the keys are column names and the values are
                Python types or SQLite data types, optionally followed by a
                string representing additional column constraints.

        Examples:
            >>> db = SQLiteDatabase({'path': ':memory:', 'timeout': 5})
            >>> db.create_table('users', {'id': (int, 'PRIMARY KEY'),
                                          'name': str, 'age': int})
        """
        columns = []

        for name, dtype in schema.items():
            if isinstance(dtype, tuple):
                python_dtype, extra_info = dtype
                sqlite_dtype = self.PYTHON_SQLITE_TYPE_MAP.get(
                    python_dtype, 'TEXT')
                column_definition = f'{name} {sqlite_dtype} {extra_info}'
            elif isinstance(dtype, type):
                sqlite_dtype = self.PYTHON_SQLITE_TYPE_MAP.get(dtype, 'TEXT')
                column_definition = f'{name} {sqlite_dtype}'
            else:
                sqlite_dtype = dtype.upper() if dtype.upper(
                ) in self.SQLITE_VALID_TYPES else 'TEXT'
                column_definition = f'{name} {sqlite_dtype}'

            columns.append(column_definition)

        columns_str = ', '.join(columns)
        query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})'
        cursor = self.execute(query)

        return cursor

    def drop_table(self,
                   table_name: str,
                   if_exists: bool = True) -> sqlite3.Cursor:
        """
        Drop a table from the database.

        Args:
            table_name (str): The name of the table to drop.
            if_exists (bool): Whether to only drop the table if it exists.

        Examples:
            >>> db = SQLiteDatabase('path/to/database.db')
            >>> db.connect()
            >>> db.drop_table('users')
        """
        if if_exists:
            query = f'DROP TABLE IF EXISTS {table_name}'
        else:
            query = f'DROP TABLE {table_name}'
        cursor = self.execute(query)

        return cursor

    def insert(self, table_name: str, data: dict) -> sqlite3.Cursor:
        """
        Insert a single row of data into the specified table.

        Args:
            table_name (str): The name of the table where the data should be
                inserted.
            data (dict): A dictionary where the keys are column names and the
                values are the data to be inserted.

        Examples:
            >>> db = SQLiteDatabase('path/to/database.db')
            >>> db.connect()
            >>> db.insert('users', {'name': 'Alice', 'age': 25})
        """
        keys = ', '.join(data.keys())
        values_placeholder = ', '.join('?' * len(data))
        values = tuple(data.values())
        query = f'INSERT INTO {table_name} ({keys}) ' \
                f'VALUES ({values_placeholder})'
        cursor = self.execute(query, values)

        return cursor

    def inserts(self, table_name: str,
                data_list: List[Dict]) -> sqlite3.Cursor:
        """
        Insert multiple rows of data into the specified table.

        Args:
            table_name (str): The name of the table where the data should be
                inserted.
            data_list (List[Dict]): A list of dictionaries where each
                dictionary represents a row of data to be inserted.

        Examples:
            >>> db = SQLiteDatabase('path/to/database.db')
            >>> db.connect()
            >>> db.inserts('users',
                           [{'name': 'Alice', 'age': 25},
                            {'name': 'Bob', 'age': 30}])
        """
        keys = ', '.join(data_list[0].keys())
        values_placeholder = ', '.join('?' * len(data_list[0]))
        query = f'INSERT INTO {table_name} ({keys}) ' \
                f'VALUES ({values_placeholder})'
        cursor = self.execute(
            query,
            params=[tuple(data.values()) for data in data_list],
            execute_many=True)

        return cursor

    def delete(self, table_name: str, condition: Dict[str,
                                                      Any]) -> sqlite3.Cursor:
        """
        Delete a single row from the specified table.

        Args:
            table_name (str): The name of the table where the data should be
                deleted from.
            condition (Dict[str, Any]): A dictionary representing the SQL
                condition for which rows to delete.

        Examples:
            >>> db = SQLiteDatabase('path/to/database.db')
            >>> db.connect()
            >>> db.delete('users', {"name": "Alice"})
        """
        condition_str = ' AND '.join(
            [f"{k}='{v}'" for k, v in condition.items()])
        query = f'DELETE FROM {table_name} WHERE {condition_str}'
        cursor = self.execute(query)

        return cursor

    def deletes(self, table_name: str,
                conditions: List[Dict[str, Any]]) -> sqlite3.Cursor:
        """
        Delete multiple rows from the specified table.

        Args:
            table_name (str): The name of the table where the data should be
                deleted from.
            conditions (List[Dict[str, Any]]): A list of dictionaries, each
                representing a SQL condition for which rows to delete.

        Examples:
            >>> db = SQLiteDatabase('path/to/database.db')
            >>> db.connect()
            >>> db.deletes('users', [{"name": "Alice"}, {"age": "<30"}])
        """
        condition_strs = [
            ' AND '.join([f"{k}='{v}'" for k, v in cond.items()])
            for cond in conditions
        ]
        condition_query = ' OR '.join([f'({cond})' for cond in condition_strs])
        query = f'DELETE FROM {table_name} WHERE {condition_query}'
        cursor = self.execute(query)

        return cursor

    def update(self, table_name: str, record: Dict[str, Any],
               condition: Dict[str, Any]) -> sqlite3.Cursor:
        """
        Update a single row in the specified table based on the given
        condition.

        Args:
            table_name (str): The name of the table to update.
            record (Dict[str, Any]): A dictionary representing the new values
                for the record.
            condition (Dict[str, Any]): A dictionary representing the SQL
                condition to identify which record to update.

        Examples:
            >>> db = SQLiteDatabase('path/to/database.db')
            >>> db.connect()
            >>> db.update('users', {'age': 26}, {'name': 'Alice'})
        """
        set_str = ', '.join([f'{k} = ?' for k in record.keys()])
        where_str = ' AND '.join([f'{k} = ?' for k in condition.keys()])
        query = f'UPDATE {table_name} SET {set_str} WHERE {where_str}'
        values = tuple(list(record.values()) + list(condition.values()))
        cursor = self.execute(query, values)

        return cursor

    def updates(self, table_name: str, records: list,
                conditions: list) -> sqlite3.Cursor:
        """
        Update multiple rows in the specified table based on the given
        conditions.

        Args:
            table_name (str): The name of the table to update data in.
            records (list): A list of dictionaries where each dictionary
                contains the data to update.
            conditions (list): A list of dictionaries where each dictionary
                represents the SQL condition for which rows to update.

        Examples:
            >>> db = SQLiteDatabase('path/to/database.db')
            >>> db.connect()
            >>> db.updates('users',
                         [{'name': 'Alice'}, {'name': 'Bob'}],
                         [{'age': 20}, {'age': 30}])
        """
        query = f'UPDATE {table_name} SET '

        try:
            cursor = self.connection.cursor()
            for record, condition in zip(records, conditions):
                set_clause = ', '.join([f'{k} = ?' for k in record.keys()])
                where_clause = ' AND '.join(
                    [f'{k} = ?' for k in condition.keys()])
                cursor.execute(
                    query + set_clause + ' WHERE ' + where_clause,
                    list(record.values()) + list(condition.values()))
            self.commit()
        except sqlite3.Error as e:
            print(f'An error occurred while updating data: {e}')

    def select(self, table_name: str, conditions: dict = None) -> List[Dict]:
        """
        Select a single row from the specified table based on the given
        conditions.

        Args:
            table_name (str): The name of the table to select data from.
            conditions (dict, optional): A dictionary where the keys are column
                names and the values are the conditions the data must meet.

        Returns:
            List[Dict]: A list of dictionaries where each dictionary represents
                a row of selected data.

        Examples:
            >>> db = SQLiteDatabase('path/to/database.db')
            >>> db.connect()
            >>> data = db.select('users', {'name': 'Alice'})
            >>> print(data)
            [{'name': 'Alice', 'age': 25}]
        """
        if conditions is None:
            query = f'SELECT * FROM {table_name}'
        else:
            conditions_str = ' AND '.join(
                [f'{key} = ?' for key in conditions.keys()])
            query = f'SELECT * FROM {table_name} WHERE {conditions_str}'
            values = tuple(conditions.values())

        try:
            cursor = self.connection.cursor()
            if conditions is None:
                cursor.execute(query)
            else:
                cursor.execute(query, values)
            rows = self.fetch_all(cursor)
            return [dict(zip(row.keys(), row)) for row in rows]
        except sqlite3.Error as e:
            print(f'An error occurred while selecting data: {e}')
            return []

    def selects(self, table_name: str,
                conditions_list: List[Dict]) -> List[List[Dict]]:
        """
        Select multiple rows from the specified table based on the given list
        of conditions.

        Args:
            table_name (str): The name of the table to select data from.
            conditions_list (List[Dict]): A list of dictionaries where each
                dictionary represents a set of conditions the data must meet.

        Returns:
            List[List[Dict]]: A list of list of dictionaries where each list
                represents the rows of selected data for each set of
                conditions.

        Examples:
            >>> db = SQLiteDatabase('path/to/database.db')
            >>> db.connect()
            >>> data = db.selects('users', [{'name': 'Alice'}, {'age': 30}])
            >>> print(data)
            [[{'name': 'Alice', 'age': 25}], [{'name': 'Bob', 'age': 30}]]
        """
        result = []

        for conditions in conditions_list:
            if conditions is None:
                query = f'SELECT * FROM {table_name}'
            else:
                conditions_str = ' AND '.join(
                    [f'{key} = ?' for key in conditions.keys()])
                query = f'SELECT * FROM {table_name} WHERE {conditions_str}'
                values = tuple(conditions.values())

            try:
                cursor = self.connection.cursor()
                if conditions is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query, values)
                rows = self.fetch_all(cursor)
                result.append([dict(row) for row in rows])
            except sqlite3.Error as e:
                print(f'An error occurred while selecting data: {e}')
                result.append([])

        return result

    def rollback(self) -> None:
        """Rollback the current transaction."""
        if self.connection:
            try:
                self.connection.rollback()
            except sqlite3.Error as e:
                print(f'An error occurred while rolling back: {e}')

    def fetch_one(self, cursor: sqlite3.Cursor) -> Union[sqlite3.Row, None]:
        """
        Fetch the next row of a query result set, returning a single sequence,
        or None when no more data is available.

        Args:
            cursor (sqlite3.Cursor): A SQLite cursor object.

        Returns:
            Union[sqlite3.Row, None]: A Row object representing the fetched
                row, or None if no more data is available.

        Examples:
            >>> db = SQLiteDatabase({'path': 'path/to/database.db',
                                     'timeout': 5})
            >>> cursor = db.execute("SELECT * FROM users WHERE name = ?",
                                   ("Alice",))
            >>> row = db.fetch_one(cursor)
            >>> print(row)
            <sqlite3.Row object at 0x7f8a8e13dab0>
        """
        try:
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f'An error occurred while fetching data: {e}')

    def fetch_all(self, cursor: sqlite3.Cursor) -> List[sqlite3.Row]:
        """
        Fetch all remaining rows of a query result, returning a list. An empty
        list is returned when no more rows are available.

        Args:
            cursor (sqlite3.Cursor): A SQLite cursor object.

        Returns:
            List[sqlite3.Row]: A list of Row objects representing the fetched
                rows.

        Examples:
            >>> db = SQLiteDatabase({'path': 'path/to/database.db',
                                'timeout': 5})
            >>> cursor = db.execute("SELECT * FROM users")
            >>> rows = db.fetch_all(cursor)
            >>> for row in rows:
            ...     print(row)
            <sqlite3.Row object at 0x7f8a8e13dab0>
            <sqlite3.Row object at 0x7f8a8e13db90>
        """
        try:
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f'An error occurred while fetching data: {e}')

    def print_tables(self) -> None:
        """Print a list of all tables in the database."""
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            tables = self.fetch_all(cursor)
            for table in tables:
                print(table[0])
        except sqlite3.Error as e:
            print(f'An error occurred while fetching table names: {e}')

    def print_schema(self, table: str) -> None:
        """Print the schema of the specified table.

        Args:
            table: The name of the table to print the schema of.
        """
        query = f'PRAGMA table_info({table});'
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            schema = self.fetch_all(cursor)
            for column in schema:
                print(f'{column[1]} ({column[2]})')
        except sqlite3.Error as e:
            print(f'An error occurred while fetching the schema: {e}')

    def print_row(self, table: str, condition: str) -> None:
        """Print a single row from the specified table based on the condition.

        Args:
            table: The name of the table to print a row from.
            condition: The condition to identify the row to print.
        """
        query = f'SELECT * FROM {table} WHERE {condition};'
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            row = self.fetch_one(cursor)
            if row:
                print(dict(row))
            else:
                print(f'No row found with condition: {condition}')
        except sqlite3.Error as e:
            print(f'An error occurred while fetching the row: {e}')

    def print_rows(self,
                   table: str,
                   condition: str = None,
                   limit: int = None) -> None:
        """Print multiple rows from the specified table based on the condition.

        Args:
            table: The name of the table to print rows from.
            condition: The condition to identify the rows to print. If None,
                all rows are printed.
            limit: The maximum number of rows to print. If None, all matching
                rows are printed.
        """
        query = f'SELECT * FROM {table}'
        if condition:
            query += f' WHERE {condition}'
        if limit:
            query += f' LIMIT {limit}'
        query += ';'
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = self.fetch_all(cursor)
            for row in rows:
                print(dict(row))
        except sqlite3.Error as e:
            print(f'An error occurred while fetching the rows: {e}')
