import pytest
import os
import sys
import tempfile
from io import BytesIO

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, init_db, extract_metadata

@pytest.fixture
def client():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Use a temporary database
    with app.app_context():
        # Override the DB_FILE for tests is tricky without refactoring app.py to accept config
        # For now, we will test the routes that don't depend heavily on persistent state
        # or mock the db connection if needed.
        # Actually app.py uses a global DB_FILE constant, which is hard to patch.
        # However, for a simple smoke test, we can test the metadata logic and basic page loads.
        pass

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def test_index_route(client):
    """Test that the index page loads."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Metadata' in rv.data

def test_metadata_extraction_dummy():
    """Test metadata extraction logic with a dummy file."""
    # Create a dummy file object
    data = b"Hello World"
    file = BytesIO(data)
    file.filename = "test.txt"
    
    metadata = extract_metadata(file)
    
    assert metadata['filename'] == "test.txt"
    assert metadata['file_type'] == "txt"
    assert metadata['size_kb'] > 0
    assert 'created_time' in metadata

def test_upload_flow(client):
    """Test the file upload endpoint (mocking DB interactions would be better, but smoke test is fine)."""
    # This might fail if the DB isn't initialized, but app.py initializes it on import/main.
    # We'll just check if the route accepts POST.
    data = {
        'files[]': (BytesIO(b"test file content"), 'test.txt')
    }
    rv = client.post('/process-files', data=data, content_type='multipart/form-data')
    assert rv.status_code == 200
    assert b'redirect_url' in rv.data
