npm install -g @opensea/cli
opensea login --scopes read:favorites
opensea auth status
opensea whoami

: "${OPENSEA_API_KEY:?Set OPENSEA_API_KEY in the environment}"
: "${OPENSEA_PRIVATE_KEY:?Set OPENSEA_PRIVATE_KEY in the environment}"
export DROP_SLUG="ltf"

opensea login --private-key --scopes read:eligibility
opensea whoami
opensea drops eligibility "$DROP_SLUG"
opensea auth revoke 
