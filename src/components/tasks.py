import time
import asyncio

from nextcord import Color, Embed, TextChannel
from nextcord.errors import HTTPException
from ..utilities.colored_printing import colorized_print
from ..utilities.atm_leaderboard import get_atms
from ..utilities.file_managers import load_file, save_file
from ..utilities.cftools import check_gameserver



killfeed_colors = {
    "player_kill": Color.red(),
    "friendly_fire": Color.orange()
}


async def _update_ATM_leaderboard(bot):
    # colorized_print("TASK", "Updating ATM Leaderboard")
    guild = bot.get_guild(bot.server_settings["guild_id"])
    atm_channel = guild.get_channel(bot.server_settings["atm_leaderboard_channel"])
    atm_leaderboard_message = atm_channel.get_partial_message(bot.server_settings["atm_leaderboard_message_id"])

    while True:
        timestamp = int(time.time()) + bot.server_settings["update_interval"] + 1
        atms = get_atms()
        embed = Embed(title="Top ATMs", description=f"Highest ATMs\n(refreshing <t:{timestamp}:R>)", color=Color.yellow())

        first = atms[0]
        second = atms[1]
        third = atms[2]

        embed.add_field(name="<:firstplace:1208505266111250472>", value=f"**{first[0]}**\n`$"+ '{:,}'.format(first[1]) + '`')
        embed.add_field(name="<:secondplace:1208505264576266300>", value=f"**{second[0]}**\n`$"+ '{:,}'.format(second[1]) + '`')
        embed.add_field(name="<:thirdplace:1208505263204605993>", value=f"**{third[0]}**\n`$"+ '{:,}'.format(third[1]) + '`')

        runner_ups = ""
        pos = 4
        for atm in atms[3:]:
            runner_ups += f"{pos}ᵗʰ **{atm[0]}**: `$"+ '{:,}'.format(atm[1]) + '`\n'
            pos += 1
            
        embed.add_field(name="Runner Ups", value=runner_ups)
        await atm_leaderboard_message.edit(embed=embed)

        await asyncio.sleep(bot.server_settings["update_interval"])
        colorized_print("DEBUG", "Updating ATM Leaderboard")


async def _update_killfeed(bot):
    # colorized_print("TASK", "Updating Killfeed Leaderboard")
    guild = bot.get_guild(bot.server_settings["guild_id"])
    killfeed_channel = guild.get_channel(bot.server_settings["killfeed_channel"])
    
    while True:
        killfeed = load_file("../dz-master/servers/1/profiles/LBmaster/Data/Killfeed/history.json")
        history = load_file("src/temp/killfeed_history.json")
        last_check = history["last_feed_date"]
        found_entries = []
        for killfeed_entry in killfeed:
            if killfeed_entry["victimName"] in ("BOT", ""):
                continue
            elif killfeed_entry["killerName"] in ("BOT", ""):
                continue
            elif killfeed_entry["date"] <= last_check:
                continue
            found_entries.append(killfeed_entry)

        if len(found_entries) == 0:
            await asyncio.sleep(bot.server_settings["update_interval"])
            continue
        
        for entry in found_entries:
            friendly_fire_notice = ""
            color = "player_kill"

            same_group = entry['killerGroup'] == entry['victimGroup']
            in_group = entry['killerGroup'] != ""
            
            if same_group and in_group:
                friendly_fire_notice = "**Friendly Fire**\n"
                color = "friendly_fire"
            last_check = entry["date"]
            embed = Embed(
                title=f"{entry['killerGroup']} {entry['killerName']} Killed {entry['victimGroup']} {entry['victimName']}", 
                description=f"{friendly_fire_notice}From a distance of {entry['distance']}m, <t:{entry["date"]}:R>", color=killfeed_colors[color]
            )
            attachments = "Stock"
            if len(entry["attachments"]) > 0:
                attachments = ""
                for attachment in entry["attachments"]:
                    if attachment == "":
                        continue
                    attachments += f"• {attachment.replace('_', ' ')}\n"
            embed.add_field(name=f"Weapon `{entry['killerItemClassname'].replace('_', ' ')}`", value=attachments)

            await killfeed_channel.send(embed=embed)
        history["last_feed_date"] = last_check
        save_file("src/temp/killfeed_history.json", history)
        await asyncio.sleep(bot.server_settings["update_interval"])
        colorized_print("DEBUG", "Updating kill feed")


async def _check_gameserver(bot):
    guild = bot.get_guild(bot.server_settings["guild_id"])
    status_channel:TextChannel = guild.get_channel(bot.server_settings["status_channel"])
    status_message = status_channel.get_partial_message(bot.server_settings["status_message_id"])
    await status_channel.edit(name="🔵〕server-status")
    cftools_settings = load_file("src/settings/cftools.json")
    is_offline = False
    while True:
        # colorized_print("TASK", "Updating Server Status")
        result = check_gameserver()
        server_name = result[cftools_settings["server_id"]]["name"]
        map_name = result[cftools_settings["server_id"]]["map"]
        if result:
            is_online = result[cftools_settings["server_id"]]["online"]
            try:
                if is_online:
                    is_offline = False
                    player_count = result[cftools_settings["server_id"]]["status"]["players"]
                    current_time = result[cftools_settings["server_id"]]["environment"]["time"]
                    embed = Embed(title=f"{server_name} - {map_name}", description=f"Server is online 🟢 as of :<t:{int(time.time())}:R>", color=Color.green())
                    embed.add_field(name="Players Online", value=player_count)
                    embed.add_field(name="Current Time", value=current_time)
                    await status_message.edit(embed=embed)
                elif is_offline:
                    await asyncio.sleep(1)
                    continue
                else:
                    is_offline = True
                    embed = Embed(title=f"{server_name} - {map_name}", description=f"Server is offline 🔴 as of :<t:{int(time.time())}:R>", color=Color.red())
                    await status_message.edit(embed=embed)
            except HTTPException as e:
                colorized_print("ERROR", e)

        await asyncio.sleep(bot.server_settings["update_interval"] * 2)
        colorized_print("DEBUG", "Updating server status")