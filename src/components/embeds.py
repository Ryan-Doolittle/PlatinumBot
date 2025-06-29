import time
from nextcord import Interaction, Embed, Color, Member
from ..utilities.colored_printing import colorized_print

async def bot_log_embed(bot, interaction:Interaction, command:str, color:Color, comment:str=None, thumbnail_url:str=None):
    bot_log_channel = interaction.guild.get_channel(int(bot.server_settings["bot_log_channel"]))
    embed = Embed(title=f"{interaction.user.display_name} used {command}", description=f"<t:{int(time.time())}:R>", color=color)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)
    if comment:
        embed.add_field(name="Comment", value=comment)
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    await bot_log_channel.send(embed=embed)

def not_an_admin():
    colorized_print("WARNING", "User is not an admin!")
    embed = Embed(title="You do not have access to this functionality!", color=Color.orange())
    return embed


def command_failed_no_valid_roles():
    colorized_print("FAIL", "User does not have any valid roles for this command!")
    embed = Embed(title="You do not have access to this command!", color=Color.yellow())
    return embed


def already_registered():
    colorized_print("FAIL", "User is already registered.")
    embed = Embed(title="You are already registered, no additional action required!", color=Color.yellow())
    return embed


def player_not_whitelisted():
    colorized_print("FAIL", "User is not whitelisted.")
    embed = Embed(title="You have not been whitelisted yet, open a whitelist request.", description="This command is intended for  users that have already been whitelisted prior to the register command.\n Once you have been whitelisted you will not need to enter this command.", color=Color.yellow())
    return embed


def player_has_been_registered(incentive_amount:int):
    colorized_print("INFO", "Whitelisted User has been registered.")
    embed = Embed(title="You have successfully been registered!", description='${:,}'.format(incentive_amount) + " has been added to your ATM", color=Color.green())
    return embed