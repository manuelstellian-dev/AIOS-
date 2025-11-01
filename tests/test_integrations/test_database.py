"""Tests for Database Integration"""
import pytest
import tempfile
import os

# Import database integration
try:
    from venom.integrations.database import DatabaseIntegration
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    DatabaseIntegration = None


@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="Database integration not available")
def test_sqlite_operations():
    """Test SQLite database operations"""
    # Use in-memory database for testing
    db = DatabaseIntegration(db_type='sqlite', database=':memory:')
    
    # Test connection
    assert db.connect() is True
    
    # Create table
    schema = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'name': 'TEXT NOT NULL',
        'email': 'TEXT'
    }
    assert db.create_table('users', schema) is True
    
    # Check table exists
    assert db.table_exists('users') is True
    assert db.table_exists('nonexistent') is False
    
    # Insert data
    row_id = db.insert('users', {'name': 'Alice', 'email': 'alice@example.com'})
    assert row_id > 0
    
    # Fetch data
    user = db.fetch_one('SELECT * FROM users WHERE name = ?', ('Alice',))
    assert user is not None
    assert user['name'] == 'Alice'
    assert user['email'] == 'alice@example.com'
    
    # Close connection
    db.disconnect()


@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="Database integration not available")
def test_insert_update_delete():
    """Test insert, update, and delete operations"""
    db = DatabaseIntegration(db_type='sqlite', database=':memory:')
    db.connect()
    
    # Create table
    db.create_table('products', {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'name': 'TEXT',
        'price': 'REAL',
        'stock': 'INTEGER'
    })
    
    # Insert multiple products
    db.insert('products', {'name': 'Widget', 'price': 19.99, 'stock': 100})
    db.insert('products', {'name': 'Gadget', 'price': 29.99, 'stock': 50})
    db.insert('products', {'name': 'Doohickey', 'price': 9.99, 'stock': 200})
    
    # Fetch all products
    products = db.fetch_all('SELECT * FROM products')
    assert len(products) == 3
    
    # Update product
    affected = db.update(
        'products',
        {'price': 24.99, 'stock': 75},
        {'name': 'Widget'}
    )
    assert affected == 1
    
    # Verify update
    widget = db.fetch_one('SELECT * FROM products WHERE name = ?', ('Widget',))
    assert widget['price'] == 24.99
    assert widget['stock'] == 75
    
    # Delete product
    affected = db.delete('products', {'name': 'Gadget'})
    assert affected == 1
    
    # Verify deletion
    products = db.fetch_all('SELECT * FROM products')
    assert len(products) == 2
    
    db.disconnect()


@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="Database integration not available")
def test_parameterized_queries():
    """Test parameterized queries for SQL injection prevention"""
    db = DatabaseIntegration(db_type='sqlite', database=':memory:')
    db.connect()
    
    # Create table
    db.create_table('users', {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'username': 'TEXT',
        'email': 'TEXT'
    })
    
    # Insert with parameterized query
    db.insert('users', {
        'username': 'testuser',
        'email': 'test@example.com'
    })
    
    # Query with parameters (safe from SQL injection)
    user = db.fetch_one(
        'SELECT * FROM users WHERE username = ? AND email = ?',
        ('testuser', 'test@example.com')
    )
    assert user is not None
    assert user['username'] == 'testuser'
    
    # Try potentially malicious input (should be safely escaped)
    malicious = "'; DROP TABLE users; --"
    user = db.fetch_one('SELECT * FROM users WHERE username = ?', (malicious,))
    assert user is None  # Should not find user, and table should still exist
    
    # Verify table still exists
    assert db.table_exists('users') is True
    
    db.disconnect()


@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="Database integration not available")
def test_table_management():
    """Test table creation and existence checking"""
    db = DatabaseIntegration(db_type='sqlite', database=':memory:')
    db.connect()
    
    # Create multiple tables
    db.create_table('table1', {'id': 'INTEGER PRIMARY KEY', 'data': 'TEXT'})
    db.create_table('table2', {'id': 'INTEGER PRIMARY KEY', 'value': 'INTEGER'})
    
    # Check tables exist
    assert db.table_exists('table1') is True
    assert db.table_exists('table2') is True
    assert db.table_exists('table3') is False
    
    # Create table with IF NOT EXISTS (should not error)
    db.create_table('table1', {'id': 'INTEGER PRIMARY KEY', 'data': 'TEXT'})
    assert db.table_exists('table1') is True
    
    db.disconnect()


@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="Database integration not available")
def test_transaction_support():
    """Test transaction support with context manager"""
    db = DatabaseIntegration(db_type='sqlite', database=':memory:')
    db.connect()
    
    # Create table
    db.create_table('accounts', {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'name': 'TEXT',
        'balance': 'REAL'
    })
    
    # Insert initial data
    db.insert('accounts', {'name': 'Alice', 'balance': 1000.0})
    db.insert('accounts', {'name': 'Bob', 'balance': 500.0})
    
    # Test successful transaction
    try:
        with db.transaction():
            # Transfer money from Alice to Bob
            db.update('accounts', {'balance': 800.0}, {'name': 'Alice'})
            db.update('accounts', {'balance': 700.0}, {'name': 'Bob'})
    except Exception:
        pass
    
    # Verify changes were committed
    alice = db.fetch_one('SELECT * FROM accounts WHERE name = ?', ('Alice',))
    bob = db.fetch_one('SELECT * FROM accounts WHERE name = ?', ('Bob',))
    assert alice['balance'] == 800.0
    assert bob['balance'] == 700.0
    
    # Test rollback on error
    try:
        with db.transaction():
            db.update('accounts', {'balance': 600.0}, {'name': 'Alice'})
            # Simulate error
            raise ValueError("Transaction error")
            db.update('accounts', {'balance': 900.0}, {'name': 'Bob'})
    except ValueError:
        pass
    
    # Verify rollback occurred
    alice = db.fetch_one('SELECT * FROM accounts WHERE name = ?', ('Alice',))
    bob = db.fetch_one('SELECT * FROM accounts WHERE name = ?', ('Bob',))
    assert alice['balance'] == 800.0  # Should not have changed
    assert bob['balance'] == 700.0    # Should not have changed
    
    db.disconnect()


@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="Database integration not available")
def test_context_manager():
    """Test database as context manager"""
    # Create temp database file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        # Use database as context manager
        with DatabaseIntegration(db_type='sqlite', database=db_path) as db:
            db.create_table('test', {'id': 'INTEGER PRIMARY KEY', 'value': 'TEXT'})
            db.insert('test', {'value': 'test_data'})
            
            # Query inside context
            row = db.fetch_one('SELECT * FROM test')
            assert row is not None
            assert row['value'] == 'test_data'
        
        # Connection should be closed now
        # Verify by opening again
        db2 = DatabaseIntegration(db_type='sqlite', database=db_path)
        db2.connect()
        row = db2.fetch_one('SELECT * FROM test')
        assert row is not None
        assert row['value'] == 'test_data'
        db2.disconnect()
        
    finally:
        # Clean up temp file
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="Database integration not available")
def test_multiple_database_types():
    """Test that different database types are supported"""
    # SQLite should always work
    db_sqlite = DatabaseIntegration(db_type='sqlite', database=':memory:')
    assert db_sqlite.connect() is True
    db_sqlite.disconnect()
    
    # PostgreSQL and MySQL require external libraries
    # Test that they can be initialized (even if connection fails)
    try:
        db_pg = DatabaseIntegration(
            db_type='postgresql',
            host='localhost',
            database='test',
            user='test',
            password='test'
        )
        # Connection may fail, but initialization should work
        assert db_pg.db_type == 'postgresql'
    except ImportError:
        # PostgreSQL library not available - this is OK
        pass
    
    try:
        db_mysql = DatabaseIntegration(
            db_type='mysql',
            host='localhost',
            database='test',
            user='test',
            password='test'
        )
        # Connection may fail, but initialization should work
        assert db_mysql.db_type == 'mysql'
    except ImportError:
        # MySQL library not available - this is OK
        pass
