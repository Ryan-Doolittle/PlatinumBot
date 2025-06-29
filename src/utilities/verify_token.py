import requests

def verify_discord_token(token):
    headers = {
        'Authorization': f'Bot {token}'
    }
    try:
        response = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
        if response.status_code == 200:
            print("Token is valid.")
            return True
        else:
            print("Token is invalid.")
            return False
    except Exception as e:
        print(f"Error verifying token: {e}")
        return False