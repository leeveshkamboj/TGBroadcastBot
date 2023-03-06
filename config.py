import os
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    token = os.environ.get("TOKEN", None)
    api_id = os.environ.get("API_ID", None)
    api_hash = os.environ.get("API_HASH", None)
    log_id = int(os.environ.get("LOG_ID", 0))
    start_msg = os.environ.get("START_MSG", None)
    ownerID = os.environ.get("OWNER_ID", [])
    if ownerID:
        ownerID = [int(ID) for ID in ownerID.split("|")]
