import subprocess
import webbrowser
import json
import re
from difflib import get_close_matches
import ctypes

# Load commands
with open("commands.json", "r", encoding="utf-8") as f:
    COMMANDS = json.load(f)

CURRENT_CONTEXT = None

# Misheard / common word corrections
CORRECTIONS = {
    "blue to": "bluetooth",
    "blue": "bluetooth",
    "blutooth": "bluetooth",
    "bright": "brightness",
    "seting": "settings",
    "netwok": "network"
}

EXIT_VARIANTS = ["exit", "quit", "leave", "closeapp"]

def normalize(text):
    text = text.lower()
    for wrong, correct in CORRECTIONS.items():
        text = text.replace(wrong, correct)
    fillers = ["please", "can you", "for me", "just", "and", "the"]
    for f in fillers:
        text = text.replace(f, "")
    return text.strip()

def flatten_commands(d, parent_key=""):
    """Flatten nested dict to single-level keys for fuzzy matching"""
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key} {k}".strip()
        if isinstance(v, dict):
            items.update(flatten_commands(v, new_key))
        else:
            items[new_key] = v
    return items

flat_commands = flatten_commands(COMMANDS)

def run_command(cmd):
    if isinstance(cmd, str):
        if cmd.startswith("http"):
            webbrowser.open(cmd)
        elif cmd.endswith(".ps1"):
            subprocess.Popen(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", cmd], shell=True)
        else:
            subprocess.Popen(cmd, shell=True)
    else:
        print(f"Cannot run command: {cmd}")

def is_exit_command(text):
    return any(word in text for word in EXIT_VARIANTS)

def execute_command(command_text):
    global CURRENT_CONTEXT
    command_text = normalize(command_text)
    print(f"Processed: {command_text}")

    # =========================
    # Exit apps directly
    # =========================
    if is_exit_command(command_text):
        if command_text in flat_commands:
            exe_name = flat_commands[command_text]
            subprocess.Popen(f"taskkill /f /im {exe_name}", shell=True)
            print(f"Exited: {exe_name}")
        else:
            print(f"No mapped executable for: {command_text}")
        return True

    # =========================
    # Mute/unmute
    # =========================
    if "mute" in command_text or "unmute" in command_text:
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
        print("Mute/Unmute executed")
        return True

    # =========================
    # Direct exact match
    # =========================
    if command_text in flat_commands:
        run_command(flat_commands[command_text])
        CURRENT_CONTEXT = None
        print(f"Executed: {command_text}")
        return True

    # =========================
    # Fuzzy match (aggressive)
    # =========================
    matches = get_close_matches(command_text, list(flat_commands.keys()), n=1, cutoff=0.5)
    if matches:
        run_command(flat_commands[matches[0]])
        CURRENT_CONTEXT = None
        print(f"Executed (fuzzy): {matches[0]}")
        return True

    # =========================
    # Keyword match (any word in input matching a command key)
    # =========================
    for key, cmd in flat_commands.items():
        key_words = key.split()
        if any(word in command_text for word in key_words):
            run_command(cmd)
            CURRENT_CONTEXT = None
            print(f"Executed (keyword match): {key}")
            return True

    print(f"No matching command for: {command_text}")
    return False