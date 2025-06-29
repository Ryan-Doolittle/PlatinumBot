import json
from .file_managers import load_file, save_file


def get_player_info(discord_id:int, which:str):
    player_info_list = load_file("users/whitelisted_users.json")
    player = None
    for player_info in player_info_list:
        if player_info["discord_id"] == discord_id:
            player = player_info
    if player:
        return player[which]


def get_player_atm(discord_id):
    steam64_id = get_player_info(discord_id, "steam64_id")
    atm = load_file(f"../dz-master/servers/1/profiles/LBmaster/Data/LBBanking/Players/{steam64_id}.json")
    return atm


def give_player_money(discord_id, amount):
    steam64_id = get_player_info(discord_id, "steam64_id")
    atm = get_player_atm(steam64_id)
    if atm:
        atm["currentMoney"] += amount
    save_file(f"../dz-master/servers/1/profiles/LBmaster/Data/LBBanking/Players/{steam64_id}.json", atm)
