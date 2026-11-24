# Account creation and login functions
# CYSE 250 Milestone 3

import os
import threading
from encryption import encrypt

CIPHER_KEY = 4
ACCOUNT_FILE = "accounts.txt"

_account_lock = threading.Lock()


def load_accounts():
    """Reads accounts.txt and returns a dictionary of username to encrypted password."""
    accounts = {}
    if not os.path.exists(ACCOUNT_FILE):
        return accounts
    with open(ACCOUNT_FILE, "r") as file:
        for line in file:
            line = line.strip()
            if line:
                username, encrypted_password = line.split(",", 1)
                accounts[username] = encrypted_password
    return accounts


def create_account(username, password):
    """Creates a new account if the username is not already taken."""
    with _account_lock:
        accounts = load_accounts()
        if not username or not password:
            return False, "Username and password cannot be blank."
        if username in accounts:
            return False, "That username already exists."
        encrypted_password = encrypt(password, CIPHER_KEY)
        with open(ACCOUNT_FILE, "a") as file:
            file.write(f"{username},{encrypted_password}\n")
        return True, "Account created successfully!"


def verify_login(username, password):
    """Checks a username and password against the stored accounts."""
    accounts = load_accounts()
    if username not in accounts:
        return False, "Invalid username or password."
    encrypted_attempt = encrypt(password, CIPHER_KEY)
    if encrypted_attempt == accounts[username]:
        return True, f"Login successful! Welcome back, {username}."
    return False, "Invalid username or password."
