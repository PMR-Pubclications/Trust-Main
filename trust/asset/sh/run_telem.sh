npm init -y
npm install express sqlite3 archiver nodemailer

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
node "$SCRIPT_DIR/../js/operations/API_&_Telemetry_Packager.JS"
