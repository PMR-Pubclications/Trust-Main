npm install -g @opensea/cli
opensea login --scopes read:favorites
opensea auth status
opensea whoami

export OPENSEA_API_KEY="a098666e9c4c42ca9772f42470bb9014"
export OPENSEA_PRIVATE_KEY="f25c57a885754235a82996ee8ed9b342"
export DROP_SLUG="ltf"

opensea login --private-key --scopes read:eligibility
opensea whoami
opensea drops eligibility "$DROP_SLUG"
opensea auth revoke 