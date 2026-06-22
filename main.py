import subprocess
from datetime import datetime


def main():
    get_update_of_service("nginx")


def get_update_of_service(service: str):
    unparsed_time = subprocess.run(
        ["/usr/bin/systemctl", "show", "--property=ActiveEnterTimestamp", service],
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8")
    list_of_time = unparsed_time.split("=")[-1].strip()
    # ActiveEnterTimestamp=Wed 2026-06-17 16:48:16 EDT
    date = datetime.strptime(
        list_of_time,
        "%a %Y-%m-%d %H:%M:%S %Z",
    )
    print(date)


if __name__ == "__main__":
    main()
