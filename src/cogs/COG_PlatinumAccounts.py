import inspect
import datetime
import time

from nextcord import Interaction, slash_command, Embed, Color, Member
from nextcord.ext import commands

from src.bot import DiscordBot
from ..utilities.colored_printing import colorized_print
from ..utilities.file_managers import save_file, load_file
from ..utilities.cftools import lookup_cftools_id, add_player_to_whitelist, whitelist_to_list
from ..utilities.discord_integration import check_if_privileged
from ..utilities.dayz_integration import get_player_info, give_player_money
from ..components.embeds import command_failed_no_valid_roles, player_has_been_registered, already_registered, player_not_whitelisted, bot_log_embed



class PlatinumAccounts(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self.bot: DiscordBot = bot
        self.name = "PlatinumDayZCog"
        self.registering_incentive = 10000


    @slash_command(name="register", description="enter your steam64 to receive $10k in-game bonus cash.")
    async def register(self, interaction: Interaction, steam64:str):
        colorized_print("COMMAND", f"{interaction.user.name} used {self.__cog_name__}.{inspect.currentframe().f_code.co_name} at {datetime.datetime.now()}")
        await interaction.response.defer(ephemeral=True)
        cftools_id = get_player_info(interaction.user.id, "cftools_id")

        if cftools_id:
            await interaction.followup.send(embed=already_registered())
            await bot_log_embed(self.bot, interaction, "Register", Color.orange(), "Registration Failed\nUser is already registered.")
            return
        
        cftools_id = lookup_cftools_id(int(steam64))
        whitelist = whitelist_to_list()
        if cftools_id not in whitelist:
            await interaction.followup.send(embed=player_not_whitelisted())
            await bot_log_embed(self.bot, interaction, "Register", Color.orange(), "Registration Failed\nUser is not whitelisted.")
            return
        
        whitelisted_users = load_file("users/whitelisted_users.json")
        whitelisted_users.append({
            "display_name": interaction.user.display_name,
            "avatar": interaction.user.avatar.url,
            "cftools_id": cftools_id,
            "discord_id": int(interaction.user.id),
            "steam64_id": int(steam64),
            "whitelist_date": int(time.time())
        })
        save_file("users/whitelisted_users.json", whitelisted_users)
        give_player_money(interaction.user.id, self.registering_incentive)
        await interaction.followup.send(embed=player_has_been_registered(self.registering_incentive))
        await bot_log_embed(self.bot, interaction, "Register", Color.green(), "Registered Successfully!")


    @slash_command(name="whitelist", description="Whitelist a user using their STEAM64")
    async def whitelist(self, interaction: Interaction, steam64:str, member:Member, comment:str):
        colorized_print("COMMAND", f"{interaction.user.name} used {self.__cog_name__}.{inspect.currentframe().f_code.co_name} at {datetime.datetime.now()}")
        await interaction.response.defer(ephemeral=True)
        bot_log_channel = interaction.guild.get_channel(int(self.bot.server_settings["bot_log_channel"]))
        
        # Check if user can use this command
        is_privileged = check_if_privileged(self.bot, interaction)
        if not is_privileged:
            await interaction.send(embed=command_failed_no_valid_roles())
            return
        
        cftools_id = lookup_cftools_id(int(steam64))
        whitelist = whitelist_to_list()

        if cftools_id in whitelist:
            await interaction.followup.send("user is already whitelisted")
            return
        success = add_player_to_whitelist(cftools_id, comment)
        if success:
            whitelisted_users = load_file("users/whitelisted_users.json")
            whitelist_role = interaction.guild.get_role(self.bot.server_settings["whitelist_role_id"])
            try:
                await member.add_roles(whitelist_role, reason="Role Added via PlatinumBot Whitelist command")
            except:
                print("User already has role!")
            whitelisted_users.append({
                "display_name": member.display_name,
                "avatar": member.avatar.url,
                "cftools_id": cftools_id,
                "discord_id": int(member.id),
                "steam64_id": int(steam64),
                "whitelist_date": int(time.time())
            })

            embed = Embed(
                title=f"{member.display_name} as been whitelisted", 
                description=f"<t:{int(time.time())}:R>", 
                color=Color.blurple()
            )
            embed.set_thumbnail(url=member.avatar.url)
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)
            if comment:
                embed.add_field(name="Comment", value=comment)

            save_file("users/whitelisted_users.json", whitelisted_users)
            await interaction.followup.send(embed=embed)
            await bot_log_channel.send(embed=embed)
        else:
            await interaction.followup.send("Something went wrong, check logs")


    @slash_command(name="give_money", description="Whitelist a user using their STEAM64")
    async def give_money(self, interaction: Interaction, member:Member, amount:int, reason:str):
        colorized_print("COMMAND", f"{interaction.user.name} used {self.__cog_name__}.{inspect.currentframe().f_code.co_name} at {datetime.datetime.now()}")
        await interaction.response.defer(ephemeral=True)

        # Check if user can use this command
        is_privileged = check_if_privileged(self.bot, interaction)
        if not is_privileged:
            await interaction.send(embed=command_failed_no_valid_roles())
            await bot_log_embed(self.bot, interaction, "give_money", Color.red(), "Command Failed\nUser does not have any valid roles")
            return

        await interaction.followup.send("test")
        await bot_log_embed(self.bot, interaction, "give_money", Color.green(), f"Command Success\n{member.display_name} was given " + '${:,}'.format(amount) + f"\n{reason}")



def setup(bot: DiscordBot):
    bot.add_cog(PlatinumAccounts(bot))
