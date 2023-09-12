from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class BaseDatabase(ABC):

    def __init__(self, db_config: Dict[str, Any]) -> None:
        """
        Initialize the database with the given configuration.

        Args:
            db_config (Dict[str, Any]): A dictionary containing database
                configuration parameters.
        """
        pass

    @abstractmethod
    def connect(self) -> Any:
        """Establish a connection to the database."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    def insert(self, table: str, data_dict: Dict[str, Any]) -> None:
        """Insert a single row of data into the given table."""
        pass

    def inserts(self, table: str, data_dicts: List[Dict[str, Any]]) -> None:
        """Insert multiple rows of data into the given table."""
        for data_dict in data_dicts:
            self.insert(table, data_dict)

    @abstractmethod
    def delete(self, table: str, condition: str) -> None:
        """Delete a single row of data from the given table."""
        pass

    def deletes(self, table: str, conditions: List[str]) -> None:
        """Delete multiple rows of data from the given table."""
        for condition in conditions:
            self.delete(table, condition)

    @abstractmethod
    def update(self, table: str, data_dict: Dict[str, Any],
               condition: str) -> None:
        """Update a single row of data in the given table."""
        pass

    def updates(self, table: str, data_dicts: List[Dict[str, Any]],
                conditions: List[str]) -> None:
        """Update multiple rows of data in the given table."""
        for data_dict, condition in zip(data_dicts, conditions):
            self.update(table, data_dict, condition)

    @abstractmethod
    def select(self, table: str, columns: List[str],
               condition: str) -> List[Dict[str, Any]]:
        """Select columns from a single row of the given table."""
        pass

    def selects(self, table: str, columns: List[str],
                conditions: List[str]) -> List[Dict[str, Any]]:
        """Select columns from multiple rows of the given table."""
        for condition in conditions:
            yield self.select(table, columns, condition)

    @abstractmethod
    def create_table(self, table: str, schema: Dict[str, str]) -> None:
        """Create a new table with the given schema."""
        pass

    @abstractmethod
    def drop_table(self, table: str) -> None:
        """Drop the specified table."""
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit the current transaction."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction."""
        pass

    def __enter__(self):
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context manager, handling exceptions and closing the
            connection if necessary."""
        if exc_type is not None:
            print(f'An exception of type {exc_type} occurred: {exc_value}')
        self.close()

    @abstractmethod
    def execute(self, query: str, params: Tuple[Any, ...] = ()) -> Any:
        """
        Execute a SQL query with the optional parameters.

        Args:
            query (str): The SQL query to execute.
            params (Tuple[Any, ...]): A tuple of parameters to use with
                the query. Defaults to an empty tuple.

        Returns:
            A cursor object.
        """
        pass

    @abstractmethod
    def print_tables(self) -> None:
        """
        Print a list of all tables in the database.
        """
        pass

    @abstractmethod
    def print_schema(self, table: str) -> None:
        """
        Print the schema of the specified table.

        Args:
            table (str): The name of the table to print the schema of.
        """
        pass

    @abstractmethod
    def print_row(self, table: str, condition: str) -> None:
        """
        Print a single row from the specified table based on the condition.

        Args:
            table (str): The name of the table to print a row from.
            condition (str): The condition to identify the row to print.
        """
        pass

    @abstractmethod
    def print_rows(self,
                   table: str,
                   condition: Optional[str] = None,
                   limit: Optional[int] = None) -> None:
        """
        Print multiple rows from the specified table based on the condition.

        Args:
            table (str): The name of the table to print rows from.
            condition (Optional[str]): The condition to identify the rows
                to print. If None, all rows are printed. Defaults to None.
            limit (Optional[int]): The maximum number of rows to print.
                If None, all matching rows are printed. Defaults to None.
        """
        pass
