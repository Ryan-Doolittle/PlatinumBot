import sys
import os
import asyncio
import qdarktheme
import qasync

from PyQt5.QtWidgets import QApplication, QInputDialog, QWidget, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon

from src.bot import DiscordBot

from src.utilities.resource_path import resource_path
from src.utilities import file_managers
from src.utilities.verify_token import verify_discord_token
from src.utilities.colored_printing import colorized_print

settings = file_managers.load_file(resource_path("settings/bot.json"))



class MainWindow(QWidget):
    def __init__(self, bot, loop):
        super().__init__()
        self.bot = bot
        self.loop = loop
        self.bot_running = False
        self.init_ui()


    def init_ui(self):
        if settings["DISCORD_TOKEN"] == "":
            self.prompt_token()

        self.setWindowTitle('Platinum Bot')
        self.setWindowIcon(QIcon(resource_path('img/logo.png')))
        self.setGeometry(100, 100, 250, 100)
        layout = QVBoxLayout(self)

        self.start_button = QPushButton('Start Bot', self)
        self.start_button.setStyleSheet("QPushButton { background-color: green; color: white; }")
        self.start_button.clicked.connect(self.start_bot)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Shutdown', self)
        self.stop_button.setStyleSheet("QPushButton { background-color: red; color: white; }")
        self.stop_button.clicked.connect(self.confirm_shutdown)
        layout.addWidget(self.stop_button)


    def prompt_token(self):
        token, ok = QInputDialog.getText(self, 'Enter Discord Token', 'Please enter your Discord bot token:')
        if ok:
            settings["DISCORD_TOKEN"] = token


    def start_bot(self):
        if settings["DISCORD_TOKEN"] == "":
            self.prompt_token()
            if settings["DISCORD_TOKEN"] == "":
                QMessageBox.warning(self, 'Token Required', 'No token provided. Please enter a valid token.')
                return
            if not verify_discord_token(settings["DISCORD_TOKEN"]):
                settings["DISCORD_TOKEN"] = ""
                QMessageBox.warning(self, 'Invalid Token', 'Check your input this token is invalid')
                return

        file_managers.save_file(resource_path("settings/bot.json"), settings)
        
        if not self.bot_running:
            self.start_button.setStyleSheet("QPushButton { background-color: blue; color: white; }")
            self.start_button.setText("Bot Active")
            colorized_print("DEBUG", "Scheduling bot start")
            colorized_print("DEBUG", f"Bot start loop state - running: {self.loop.is_running()}, closed: {self.loop.is_closed()}")
            asyncio.ensure_future(self.bot.start_with_tasks(settings["DISCORD_TOKEN"]), loop=self.loop)
            self.bot_running = True
        else:
            colorized_print("ERROR", "Bot is already running.")


    def confirm_shutdown(self):
        reply = QMessageBox.question(self, 'Confirm Shutdown', 'Are you sure you want to shut down?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.bot_running:
                asyncio.ensure_future(self.bot.close(), loop=self.loop)
            QApplication.quit()


def run():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    bot = DiscordBot(settings, loop=loop)  # Pass loop explicitly
    window = MainWindow(bot, loop)
    window.show()
    colorized_print("DEBUG", "Starting asyncio event loop with async")
    with loop:
        loop.run_forever()


if __name__ == "__main__":
    colorized_print("DEBUG", "Application starting, preparing the environment.")
    colorized_print("DEBUG", "Pre startup complete, starting bot warmup")
    os.makedirs("users", exist_ok=True)
    run()
