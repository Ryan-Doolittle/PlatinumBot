import requests
import time

from src.utilities.file_managers import load_file, save_file
from src.utilities.colored_printing import colorized_print

TOKEN = None
TOKEN_ISSUED_AT = 0
TOKEN_EXPIRY_SECONDS = 12 * 60 * 60
CFTOOL_SETTINGS = load_file("src/settings/cftools.json")


def lookup_cftools_id(steam_id):
    """Lookup or attempt to register CFTools ID by Steam64ID."""
    get_auth_token()
    url = f"{CFTOOL_SETTINGS['base_url']}/v1/users/lookup?identifier={steam_id}"
    headers = {
        "User-Agent": CFTOOL_SETTINGS['application_id'],
        "Authorization": f"Bearer {TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        cftools_id = data.get("cftools_id")
        if cftools_id:
            colorized_print("DEBUG", f"Found CFTools ID: {cftools_id} for Steam ID: {steam_id}")
            return cftools_id
        else:
            colorized_print("DEBUG", f"No CFTools ID found for Steam ID: {steam_id}. User must register at https://app.cftools.cloud or join the server (IP: 136.60.8.148:2302) with whitelisting disabled.")
            return None
    except requests.exceptions.HTTPError as e:
        colorized_print("DEBUG", f"Error looking up CFTools ID: {e.response.status_code} - {e.response.text}")
        colorized_print("DEBUG", "User must register at https://app.cftools.cloud or join the server with whitelisting disabled.")
        return None
    except requests.exceptions.RequestException as e:
        colorized_print("DEBUG", f"Network error: {e}")
        return None
    

def get_auth_token(force=False):
    """Authenticate and obtain a Bearer token, refreshing if expired."""
    global TOKEN, TOKEN_ISSUED_AT
    current_time = time.time()

    # Return existing token if valid and not forced
    if not force and TOKEN and (current_time - TOKEN_ISSUED_AT) < TOKEN_EXPIRY_SECONDS:
        return TOKEN

    url = f"{CFTOOL_SETTINGS['base_url']}/v1/auth/register"
    headers = {
        "User-Agent": CFTOOL_SETTINGS['application_id'],
        "Content-Type": "application/json"
    }
    payload = {
        "application_id": CFTOOL_SETTINGS['application_id'],
        "secret": CFTOOL_SETTINGS['application_secret']
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        TOKEN = data.get("token")
        if not TOKEN:
            raise ValueError("No token received from auth response")
        TOKEN_ISSUED_AT = current_time
        colorized_print("DEBUG", "Successfully obtained auth token")
        return TOKEN
    except requests.exceptions.HTTPError as e:
        colorized_print("ERROR", f"Authentication error: {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        colorized_print("ERROR", f"Network error during authentication: {e}")
        return None
    

def check_gameserver():
    """Check gameserver info using server_id."""
    url = f"{CFTOOL_SETTINGS['base_url']}/v1/gameserver/{CFTOOL_SETTINGS['server_id']}"
    headers = {"User-Agent": CFTOOL_SETTINGS['application_id']}
    try:
        response = requests.get(url, headers=headers)
        gameserver_info = response.json() if response.status_code == 200 else None
        save_file("gameserver_info.json", gameserver_info)
        return gameserver_info
    except requests.exceptions.HTTPError as e:
        colorized_print("ERROR", f"GameServer Error: {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        colorized_print("ERROR", f"Network error: {e}")
        return None


def add_new_user_to_whitelist(steam_id, comment="Added via API", expires_at=None):
    """Add a new user to the whitelist, handling unregistered users."""
    get_auth_token()
    colorized_print("DEBUG", f"Attempting to add user with Steam64 ID: {steam_id}")
    cftools_id = lookup_cftools_id(TOKEN, steam_id)
    if not cftools_id:
        return False
    return add_player_to_whitelist(TOKEN, cftools_id, comment, expires_at)


def add_player_to_whitelist(cftools_id, comment="Added via API", expires_at=None):
    """Add a player to the server whitelist."""
    get_auth_token()
    url = f"{CFTOOL_SETTINGS['base_url']}/v1/server/{CFTOOL_SETTINGS['server_api_id']}/whitelist"
    headers = {
        "User-Agent": CFTOOL_SETTINGS['application_id'],
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "cftools_id": cftools_id,
        "comment": comment
    }
    if expires_at:
        payload["expires_at"] = expires_at
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 204:
            colorized_print("DEBUG", f"Success: Added {cftools_id} to whitelist")
            return True
        else:
            colorized_print("WARNING", f"Unexpected response: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.HTTPError as e:
        colorized_print("ERROR", f"Error adding {cftools_id}: {e.response.status_code} - {e.response.text}")
        return False
    except requests.exceptions.RequestException as e:
        colorized_print("ERROR", f"Network error: {e}")
        return False


def get_whitelisted_players(cftools_id=None):
    """List all players in the server whitelist."""
    get_auth_token()
    url = f"{CFTOOL_SETTINGS['base_url']}/v1/server/{CFTOOL_SETTINGS['server_api_id']}/whitelist"
    if cftools_id:
        url += f"?cftools_id={cftools_id}"
    headers = {
        "User-Agent": CFTOOL_SETTINGS['application_id'],
        "Authorization": f"Bearer {TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as e:
        colorized_print("ERROR", f"Error listing whitelist: {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        colorized_print("ERROR", f"Network error: {e}")
        return None


def whitelist_to_list():
    whitelist_entries = get_whitelisted_players()["entries"]
    list_form = [e["user"]["cftools_id"] for e in whitelist_entries]
    return list_form