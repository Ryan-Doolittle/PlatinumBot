import os
import asyncio
import nextcord
from nextcord import Intents, Permissions, Game, Embed, File, utils, Color
from nextcord.ext import commands
import json
import time

from .components.tasks import _update_ATM_leaderboard, _update_killfeed, _check_gameserver

from .utilities.colored_printing import colorized_print
from .utilities.resource_path import resource_path
from .utilities.divider_title import divider_title
from .utilities.file_managers import load_file, save_file
from .utilities.atm_leaderboard import get_atms



class DiscordBot(commands.Bot):
    intents: Intents = Intents.default()
    intents.message_content = True
    intents.members = True
    prefix = "!"
    permissions = Permissions(permissions=8)

    def __init__(self, settings, *args, **kwargs):
        super().__init__(command_prefix=self.prefix, intents=self.intents, *args, **kwargs)
        self.name = settings["APP_NAME"]
        self.version = settings["APP_VERSION"]
        self.app_title = f"{self.name} v.{self.version}"
        self.width = len(self.app_title) + 32
        self.primary_symbol = "="
        self.secondary_symbol = "-"
        self.already_connected = False
        self.env_settings = settings
        self.server_settings = load_file("src/settings/discord.json")

        self.invite_url = None
        self.display_title()
        
        divider_title("Connections", self.width, self.secondary_symbol)

        self.add_listener(self.on_ready)
        
        self.cogs_loaded = False
        self.load_cogs()

        self.cooldowns = {}
        self.task_queue = asyncio.Queue()  # Queue for image generation tasks
        self.active_tasks = {}  # Track active tasks

        divider_title("Output", self.width, self.secondary_symbol)

    async def start_with_tasks(self, token):
        """Start the bot."""
        try:
            await self.start(token)
        except Exception as e:
            colorized_print("ERROR", f"Bot start failed: {e}")
            raise

    async def on_ready(self):
        if self.already_connected:
            return
        self.already_connected = True

        colorized_print("DEBUG", f"Logged in as {self.user} (ID: {self.user.id})")
        colorized_print("DEBUG", f"Invite Link {utils.oauth_url(client_id=self.user.id, permissions=DiscordBot.permissions)}")
        colorized_print("DEBUG", "Bot is ready")

        # Schedule tasks
        asyncio.ensure_future(_update_ATM_leaderboard(self), loop=self.loop)
        colorized_print("TASK", "ATM Leaderboard task scheduled")
        asyncio.ensure_future(_update_killfeed(self), loop=self.loop)
        colorized_print("TASK", "Kill feed task scheduled")
        asyncio.ensure_future(_check_gameserver(self), loop=self.loop)
        colorized_print("TASK", "Check game server task scheduled")


    
        # Sync slash commands
        await self.sync_all_application_commands()
        colorized_print("DEBUG", "Slash commands synced")

    def display_title(self):
        print()
        divider_title("", self.width, self.primary_symbol)
        divider_title(self.app_title, self.width, " ")
        divider_title("", self.width, self.primary_symbol)

    def load_cogs(self):
        if self.cogs_loaded:
            return
        divider_title("Cogs", self.width, self.secondary_symbol)
        cogs = [i.removesuffix(".py") for i in os.listdir(resource_path("cogs")) if i.endswith(".py")]
        for extension in cogs:
            colorized_print("COG", extension)
            try:
                self.load_extension(f"src.cogs.{extension}")
            except Exception as e:
                colorized_print("ERROR", f"Failed to load cog {extension}: {e}")
        self.cogs_loaded = True

    async def close(self):
        colorized_print("DEBUG", "Closing bot and cancelling tasks")
        for task in asyncio.all_tasks(self.loop):
            task.cancel()
        await super().close()
