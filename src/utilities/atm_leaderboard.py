import json
import os
from .file_managers import load_file

settings = load_file("src/settings/discord.json")

def get_atms(server_id:int=1, start=0, end=10):
    atms = []
    profiles_path = f"../dz-master/servers/{server_id}/profiles/LBmaster/Data/LBBanking/Players"
    for player_profile in os.listdir(profiles_path):
        if player_profile.count("backup") > 0:
            continue
        try:
            with open(f"{profiles_path}/{player_profile}", "r") as fp:
                profile:dict = json.load(fp)
                if profile["playername"] in settings["black_listed_atms"]:
                    continue
                atm = ( profile["playername"], profile["currentMoney"])
            atms.append(atm)
        except:
            continue
        atms.sort(key=lambda tup: tup[1], reverse=True)
    return atms[start:end]

import random
def test_shuffle_bank_values(atms):
    new_atms = []
    for atm in atms:
        player = atm[0]
        value = random.randint(1, 1000000)
        new_value = (player, value)
        new_atms.append(new_value)
    return new_atms
