from colorama import Fore, Style
from os import getenv
import time
from datetime import datetime

current_unix_time = int(time.time())

with open(f"src/temp/logs/{current_unix_time}.txt", "w") as log_file:
    log_file.write(f"Platinum Dayz Bot Logs\n")
    log_file.write(f"{datetime.now()}\n")
    log_file.write(f"{'=' * 30}\n")


color_map = {
    "DEBUG": {
        "color": Fore.BLUE,
        "int": 4
        },
    "TASK": {
        "color": Fore.LIGHTGREEN_EX,
        "int": 3
        },
    "INFO": {
        "color": Fore.GREEN,
        "int": 3
        },
    "COMMAND": {
        "color": Fore.GREEN,
        "int": 3
        },
    "CONN":  {
        "color": Fore.MAGENTA,
        "int": 3
        },
    "GUILD":  {
        "color": Fore.CYAN,
        "int": 3
        },
    "COG":  {
        "color": Fore.CYAN,
        "int": 2
        },
    "FAIL": {
        "color": Fore.YELLOW,
        "int": 2
        },
    "WARNING": {
        "color": Fore.YELLOW + Style.BRIGHT,
        "int": 2
        },
    "ERROR":  {
        "color": Fore.RED,
        "int": 1
        },
    "CRITICAL":  {
        "color": Fore.RED + Style.BRIGHT,
        "int": 0
        },
    }

def output_to_log(print_type:str, message:str):
    current_local_time = datetime.now()
    formatted_time = current_local_time.strftime("%H:%M:%S")
    with open(f"src/temp/logs/{current_unix_time}.txt", "a") as log_file:
        log_file.write(f"{formatted_time} | [{print_type}] {message}\n")


def colorized_print(print_type:str, message:str) -> None:
    """
    Helper function to colorize log output based on level.
    """
    debug_level = 4
    output_to_log(print_type, message)
    if color_map[print_type]["int"] <= debug_level:
        format = f'{color_map[print_type]["color"]}[{print_type}] {message}{Style.RESET_ALL}'
        print(format)