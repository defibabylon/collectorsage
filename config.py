import os
import tempfile

# Use relative paths that will work in cloud environment
DATABASE_PATH = os.getenv('DATABASE_PATH', os.path.join(os.path.dirname(__file__), 'databases'))

# For upload folder, use temp directory in cloud environments or local uploads folder
if os.getenv('UPLOAD_FOLDER'):
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
elif os.path.exists('/tmp'):  # Unix-like systems (including cloud deployments)
    UPLOAD_FOLDER = '/tmp/uploads'
else:  # Windows local development
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

# Ensure upload directory exists
try:
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        print(f"Created upload directory: {UPLOAD_FOLDER}")
    else:
        print(f"Upload directory exists: {UPLOAD_FOLDER}")
except Exception as e:
    print(f"Warning: Could not create upload directory {UPLOAD_FOLDER}: {e}")
    # Fallback to system temp directory
    UPLOAD_FOLDER = tempfile.gettempdir()
    print(f"Using fallback upload directory: {UPLOAD_FOLDER}")
