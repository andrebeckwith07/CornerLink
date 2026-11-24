# CornerLink Server
# CYSE 250 Milestone 3

import socket
import threading
import datetime
from auth import create_account, verify_login

HOST = "127.0.0.1"
PORT = 5555
LOG_FILE = "training_logs.txt"

log_lock = threading.Lock()


def save_training_log(username, rounds_sparred, rounds_bag, jump_rope, weight):
    """Saves one training session to the log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with log_lock:
        with open(LOG_FILE, "a") as file:
            file.write(f"{username},{rounds_sparred},{rounds_bag},{jump_rope},{weight},{timestamp}\n")


def get_training_history(username):
    """Returns a list of all training log entries for one boxer."""
    entries = []
    try:
        with open(LOG_FILE, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if parts[0] == username:
                    entries.append(parts)
    except FileNotFoundError:
        pass
    return entries


def build_plan(username):
    """Builds a short coaching recommendation based on the last logged session."""
    history = get_training_history(username)
    if not history:
        return "No training logs yet. Log a session first to get a plan."

    last = history[-1]
    rounds_sparred = int(last[1])

    if rounds_sparred < 3:
        return "Next session: add 2 more rounds of sparring to build your rounds back up."
    elif rounds_sparred < 6:
        return "Next session: keep sparring steady and add 10 more minutes of jump rope."
    else:
        return "Great work. Next session: hold your current rounds and focus on defense drills."


def handle_client(conn, addr):
    """Handles all messages from one connected client."""
    print(f"New connection from {addr}")
    logged_in_user = None

    with conn:
        while True:
            try:
                data = conn.recv(4096)
            except ConnectionResetError:
                break

            if not data:
                break

            message = data.decode("utf-8").strip()
            if not message:
                continue

            parts = message.split("|")
            command = parts[0].upper()

            try:
                if command == "CREATE":
                    username, password = parts[1], parts[2]
                    success, note = create_account(username, password)
                    response = f"OK|{note}" if success else f"ERROR|{note}"

                elif command == "LOGIN":
                    username, password = parts[1], parts[2]
                    success, note = verify_login(username, password)
                    if success:
                        logged_in_user = username
                    response = f"OK|{note}" if success else f"ERROR|{note}"

                elif command == "LOG":
                    if not logged_in_user:
                        response = "ERROR|You need to log in first."
                    else:
                        rounds_sparred = int(parts[1])
                        rounds_bag = int(parts[2])
                        jump_rope = int(parts[3])
                        weight = float(parts[4])
                        if rounds_sparred < 0 or rounds_bag < 0 or jump_rope < 0 or weight <= 0:
                            response = "ERROR|Numbers cannot be negative, and weight must be positive."
                        else:
                            save_training_log(logged_in_user, rounds_sparred, rounds_bag, jump_rope, weight)
                            if rounds_sparred < 3:
                                note = "Session saved. Try to get more sparring rounds in next time."
                            else:
                                note = "Session saved. Nice work today."
                            response = f"OK|{note}"

                elif command == "HISTORY":
                    if not logged_in_user:
                        response = "ERROR|You need to log in first."
                    else:
                        history = get_training_history(logged_in_user)
                        if not history:
                            response = "OK|No training logs yet."
                        else:
                            lines = []
                            for entry in history:
                                _, rounds_sparred, rounds_bag, jump_rope, weight, timestamp = entry
                                lines.append(
                                    f"{timestamp} - Sparring: {rounds_sparred} rounds, "
                                    f"Bag: {rounds_bag} rounds, Jump rope: {jump_rope} min, "
                                    f"Weight: {weight} lbs"
                                )
                            response = "OK|" + "\n".join(lines)

                elif command == "PLAN":
                    if not logged_in_user:
                        response = "ERROR|You need to log in first."
                    else:
                        response = f"OK|{build_plan(logged_in_user)}"

                elif command == "QUIT":
                    conn.sendall("OK|Goodbye.".encode("utf-8"))
                    break

                else:
                    response = "ERROR|Unknown command."

            except (ValueError, IndexError):
                response = "ERROR|That command was formatted wrong."

            conn.sendall(response.encode("utf-8"))

    print(f"Connection closed: {addr}")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"CornerLink server listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\nShutting down server.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
