npm install -g @opensea/cli
opensea login --scopes read:favorites
opensea auth status
opensea whoami

: "${OPENSEA_API_KEY:?OPENSEA_API_KEY must be set}"
: "${OPENSEA_PRIVATE_KEY:?OPENSEA_PRIVATE_KEY must be set}"
export DROP_SLUG="${DROP_SLUG:-ltf}"

opensea login --private-key --scopes read:eligibility
opensea whoami
opensea drops eligibility "$DROP_SLUG"
opensea auth revoke 

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/../py/agent_loop.py"
