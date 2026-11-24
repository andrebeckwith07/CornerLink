# CornerLink Client
# CYSE 250 Milestone 3

import socket

HOST = "127.0.0.1"
PORT = 5555


def send_command(sock, command):
    """Sends one command to the server and returns the raw response."""
    sock.sendall(command.encode("utf-8"))
    data = sock.recv(4096)
    return data.decode("utf-8")


def print_response(response):
    """Prints the message part of a server response and returns True if it was OK."""
    status, _, message = response.partition("|")
    print(message)
    return status == "OK"


def logged_in_menu(sock):
    """Menu shown after a successful login."""
    while True:
        print("\n1. Log a Training Session")
        print("2. View Training History")
        print("3. Get Next Plan")
        print("4. Log Out")
        choice = input("Choose an option: ")

        if choice == "1":
            rounds_sparred = input("Rounds sparred: ")
            rounds_bag = input("Rounds on the bag: ")
            jump_rope = input("Jump rope minutes: ")
            weight = input("Current weight: ")
            command = f"LOG|{rounds_sparred}|{rounds_bag}|{jump_rope}|{weight}"
            response = send_command(sock, command)
            print_response(response)

        elif choice == "2":
            response = send_command(sock, "HISTORY")
            print_response(response)

        elif choice == "3":
            response = send_command(sock, "PLAN")
            print_response(response)

        elif choice == "4":
            break

        else:
            print("Please enter 1, 2, 3, or 4.")


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print("Connected to CornerLink server.")

    try:
        while True:
            print("\n1. Create an Account")
            print("2. Log In")
            print("3. Quit")
            choice = input("Choose an option: ")

            if choice == "1":
                username = input("Enter a username: ")
                password = input("Enter a password: ")
                response = send_command(sock, f"CREATE|{username}|{password}")
                print_response(response)

            elif choice == "2":
                username = input("Enter your username: ")
                password = input("Enter your password: ")
                response = send_command(sock, f"LOGIN|{username}|{password}")
                if print_response(response):
                    logged_in_menu(sock)

            elif choice == "3":
                send_command(sock, "QUIT")
                break

            else:
                print("Please enter 1, 2, or 3.")
    finally:
        sock.close()
        print("Disconnected from server.")


if __name__ == "__main__":
    main()
