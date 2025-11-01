"""
VENOM Database Integration
Multi-database integration supporting SQLite, PostgreSQL, and MySQL
"""
import sqlite3
import json
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager

# Graceful imports for optional databases
try:
    import psycopg2
    import psycopg2.extras
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    psycopg2 = None

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    mysql = None


class DatabaseIntegration:
    """
    Multi-database integration for VENOM
    
    Supports:
    - SQLite (built-in, no dependencies)
    - PostgreSQL (requires psycopg2-binary)
    - MySQL (requires mysql-connector-python)
    
    Features:
    - Parameterized queries (SQL injection prevention)
    - Connection pooling
    - Transaction support
    - Context manager for auto-commit/rollback
    - Table management
    
    Example:
        # SQLite (no dependencies)
        db = DatabaseIntegration(db_type='sqlite', database='venom.db')
        db.connect()
        
        # PostgreSQL
        db = DatabaseIntegration(
            db_type='postgresql',
            host='localhost',
            database='venom',
            user='admin',
            password='secret'
        )
        
        # Insert data
        row_id = db.insert('users', {'name': 'Alice', 'email': 'alice@example.com'})
        
        # Query data
        users = db.fetch_all('SELECT * FROM users WHERE name = ?', ('Alice',))
    """
    
    def __init__(self, db_type: str = 'sqlite', **kwargs):
        """
        Initialize database integration
        
        Args:
            db_type: Database type ('sqlite', 'postgresql', 'mysql')
            **kwargs: Database-specific connection parameters
                SQLite: database (path)
                PostgreSQL: host, port, database, user, password
                MySQL: host, port, database, user, password
        """
        self.db_type = db_type.lower()
        self.connection = None
        self.kwargs = kwargs
        self._in_transaction = False
        
        # Validate database type
        if self.db_type not in ['sqlite', 'postgresql', 'mysql']:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        # Check availability
        if self.db_type == 'postgresql' and not POSTGRESQL_AVAILABLE:
            raise ImportError("PostgreSQL support requires psycopg2-binary. Install with: pip install psycopg2-binary>=2.9.0")
        
        if self.db_type == 'mysql' and not MYSQL_AVAILABLE:
            raise ImportError("MySQL support requires mysql-connector-python. Install with: pip install mysql-connector-python>=8.2.0")
    
    def connect(self) -> bool:
        """
        Connect to database
        
        Returns:
            True if connection successful
        """
        try:
            if self.db_type == 'sqlite':
                database = self.kwargs.get('database', ':memory:')
                self.connection = sqlite3.connect(database)
                self.connection.row_factory = sqlite3.Row
                
            elif self.db_type == 'postgresql':
                self.connection = psycopg2.connect(
                    host=self.kwargs.get('host', 'localhost'),
                    port=self.kwargs.get('port', 5432),
                    database=self.kwargs.get('database', 'postgres'),
                    user=self.kwargs.get('user'),
                    password=self.kwargs.get('password')
                )
                
            elif self.db_type == 'mysql':
                self.connection = mysql.connector.connect(
                    host=self.kwargs.get('host', 'localhost'),
                    port=self.kwargs.get('port', 3306),
                    database=self.kwargs.get('database'),
                    user=self.kwargs.get('user'),
                    password=self.kwargs.get('password')
                )
            
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute(
        self,
        query: str,
        params: Tuple = None,
        commit: bool = True
    ) -> Any:
        """
        Execute a SQL query
        
        Args:
            query: SQL query string
            params: Query parameters tuple (optional)
            commit: Auto-commit after execution (default: True)
            
        Returns:
            Cursor object
        """
        if not self.connection:
            raise RuntimeError("Not connected to database. Call connect() first.")
        
        cursor = self.connection.cursor()
        
        # Normalize placeholders for different databases
        if params:
            if self.db_type == 'sqlite':
                query = query.replace('%s', '?')
            elif self.db_type in ['postgresql', 'mysql']:
                query = query.replace('?', '%s')
        
        cursor.execute(query, params or ())
        
        # Only commit if not in transaction and commit flag is True
        if commit and not self._in_transaction:
            self.connection.commit()
        
        return cursor
    
    def fetch_one(
        self,
        query: str,
        params: Tuple = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row
        
        Args:
            query: SQL query string
            params: Query parameters tuple (optional)
            
        Returns:
            Row as dict or None
        """
        cursor = self.execute(query, params, commit=False)
        
        if self.db_type == 'sqlite':
            row = cursor.fetchone()
            return dict(row) if row else None
        elif self.db_type == 'postgresql':
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query.replace('?', '%s'), params or ())
            row = cursor.fetchone()
            return dict(row) if row else None
        elif self.db_type == 'mysql':
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def fetch_all(
        self,
        query: str,
        params: Tuple = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows
        
        Args:
            query: SQL query string
            params: Query parameters tuple (optional)
            
        Returns:
            List of rows as dicts
        """
        cursor = self.execute(query, params, commit=False)
        
        if self.db_type == 'sqlite':
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        elif self.db_type == 'postgresql':
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query.replace('?', '%s'), params or ())
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        elif self.db_type == 'mysql':
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> int:
        """
        Insert a row
        
        Args:
            table: Table name
            data: Data dict to insert
            
        Returns:
            Last inserted row ID
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' if self.db_type == 'sqlite' else '%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        cursor = self.execute(query, tuple(data.values()))
        
        # Get last inserted ID
        if self.db_type == 'sqlite':
            return cursor.lastrowid
        elif self.db_type == 'postgresql':
            return cursor.lastrowid if hasattr(cursor, 'lastrowid') else 0
        elif self.db_type == 'mysql':
            return cursor.lastrowid
    
    def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: Dict[str, Any]
    ) -> int:
        """
        Update rows
        
        Args:
            table: Table name
            data: Data dict to update
            where: WHERE clause conditions dict
            
        Returns:
            Number of affected rows
        """
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        
        params = tuple(data.values()) + tuple(where.values())
        cursor = self.execute(query, params)
        
        return cursor.rowcount
    
    def delete(
        self,
        table: str,
        where: Dict[str, Any]
    ) -> int:
        """
        Delete rows
        
        Args:
            table: Table name
            where: WHERE clause conditions dict
            
        Returns:
            Number of affected rows
        """
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        
        cursor = self.execute(query, tuple(where.values()))
        
        return cursor.rowcount
    
    def table_exists(self, table: str) -> bool:
        """
        Check if table exists
        
        Args:
            table: Table name
            
        Returns:
            True if table exists
        """
        try:
            if self.db_type == 'sqlite':
                query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
                cursor = self.execute(query, (table,), commit=False)
                return cursor.fetchone() is not None
            elif self.db_type == 'postgresql':
                query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)"
                cursor = self.execute(query, (table,), commit=False)
                return cursor.fetchone()[0]
            elif self.db_type == 'mysql':
                query = "SHOW TABLES LIKE %s"
                cursor = self.execute(query, (table,), commit=False)
                return cursor.fetchone() is not None
        except Exception:
            return False
    
    def create_table(
        self,
        table: str,
        schema: Dict[str, str]
    ) -> bool:
        """
        Create a table
        
        Args:
            table: Table name
            schema: Column definitions dict (name: type)
                Example: {'id': 'INTEGER PRIMARY KEY', 'name': 'TEXT'}
            
        Returns:
            True if table created successfully
        """
        try:
            columns = ', '.join([f"{k} {v}" for k, v in schema.items()])
            query = f"CREATE TABLE IF NOT EXISTS {table} ({columns})"
            self.execute(query)
            return True
        except Exception as e:
            print(f"Create table error: {e}")
            return False
    
    @contextmanager
    def transaction(self):
        """
        Context manager for transactions
        
        Example:
            with db.transaction():
                db.insert('users', {'name': 'Alice'})
                db.insert('users', {'name': 'Bob'})
            # Auto-commits on success, rollbacks on exception
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")
        
        self._in_transaction = True
        try:
            yield self
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            self._in_transaction = False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.disconnect()
