from functools import wraps
import os
import psycopg2

# Database connection parameters
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'trust_db')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'your_password')


def verify_trust_admin(admin_username):
  """Checks the legacy_trust_admins table to ensure the user is an active admin."""
  try:
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()
    cur.execute(
        'SELECT is_active, role FROM legacy_trust_admins WHERE username = %s;',
        (admin_username,),
    )
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result and result[0] is True and result[1] in ('ADMIN', 'SUPER_ADMIN'):
      return True
    return False
  except Exception as e:
    print(f'Database verification error: {e}')
    return False


def require_legacy_trust_executor(func):
  """Decorator to lock out anyone who is not the Legacy Trust Admin Executor."""

  @wraps(func)
  def wrapper(*args, **kwargs):
    # Pass the executing username or environment token
    current_admin = os.environ.get('TRUST_ADMIN_USER', None)

    if not current_admin or not verify_trust_admin(current_admin):
      raise PermissionError(
          'ACCESS DENIED: Insufficient clearance. Restricted to Legacy'
          ' Trust Admin Executor.'
      )

    print('Authentication successful: Legacy Trust Admin verified.')
    return func(*args, **kwargs)

  return wrapper


@require_legacy_trust_executor
def execute_google_drive_sync():
  """Your secure Google Drive script execution logic."""
  print('Executing authorized Google Drive sync for trust assets...')
  # Insert your Google Drive API code here


if __name__ == '__main__':
  try:
    execute_google_drive_sync()
  except PermissionError as pe:
    print(pe)
