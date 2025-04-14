import sys
from server import run_server
from client import run_client

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [server|client]")
        sys.exit(1)

    mode = sys.argv[1].lower()
    if mode == "server":
        run_server()
    elif mode == "client":
        run_client()
    else:
        print("Invalid mode. Use 'server' or 'client'.")
        sys.exit(1)

if __name__ == "__main__":
    main()