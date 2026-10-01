import io
import json
import os
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Scopes required for Google Drive API access
SCOPES = ['https://www.googleapis.com/auth/drive']

# --- Configuration ---
# Raw URL of the PDF file on GitHub
# Example: https://raw.githubusercontent.com/owner/repo/branch/filename.pdf
GITHUB_PDF_URL = (
    'https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/path/to/file.pdf'
)

# Optional: GitHub Personal Access Token if the repository is private
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', None)

# Target Google Drive File ID extracted from your link:
# https://drive.google.com/file/d/113WdbiqXFwEkefE2n5Up_8KRAXQXpCHR/view
GOOGLE_DRIVE_FILE_ID = '113WdbiqXFwEkefE2n5Up_8KRAXQXpCHR'
# ---------------------


def download_pdf_from_github(url, token=None):
  """Downloads a PDF from GitHub and returns it as an in-memory byte stream."""
  headers = {}
  if token:
    headers['Authorization'] = f'Bearer {token}'

  print(f'Fetching PDF from GitHub: {url}')
  response = requests.get(url, headers=headers)
  response.raise_for_status()

  # Return as BytesIO stream
  return io.BytesIO(response.content)


def update_google_drive_file(file_id, pdf_stream):
  """Authenticates with Google Drive and updates the specified file with new PDF content."""
  creds = None
  # The token.json file stores access and refresh tokens
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      if not os.path.exists('credentials.json'):
        raise FileNotFoundError(
            "Google Cloud 'credentials.json' file is missing. Please download"
            ' it from Google Cloud Console.'
        )
      flow = InstalledAppFlow.from_client_secrets_file(
          'credentials.json', SCOPES
      )
      creds = flow.run_local_server(port=0)

    # Save credentials for future runs
    with open('token.json', 'w') as token:
      token.write(creds.to_json())

  # Build the Drive v3 service
  service = build('drive', 'v3', credentials=creds)

  # Prepare media upload from the byte stream
  media = MediaIoBaseUpload(
      pdf_stream, mimetype='application/pdf', resumable=True
  )

  print(f'Updating Google Drive file ID: {file_id}...')
  updated_file = (
      service.files()
      .update(fileId=file_id, media_body=media, fields='id, name, webViewUrl')
      .execute()
  )

  print('File successfully updated on Google Drive!')
  print(f"File Name: {updated_file.get('name')}")
  print(f"View URL: {updated_file.get('webViewUrl')}")


if __name__ == '__main__':
  try:
    # Step 1: Download PDF from GitHub
    pdf_stream = download_pdf_from_github(GITHUB_PDF_URL, GITHUB_TOKEN)

    # Step 2: Update the specific Google Drive file
    update_google_drive_file(GOOGLE_DRIVE_FILE_ID, pdf_stream)

  except Exception as e:
    print(f'An error occurred: {e}')
