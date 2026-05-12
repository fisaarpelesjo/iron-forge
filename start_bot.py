import sys

from ironforge import banner
from ironforge import telegram_poller


def main():
    banner.print_banner()
    print("Starting training bot...\n")
    telegram_poller.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
