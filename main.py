import subprocess
from datetime import datetime
import json


def main():
    get_uptime_of_systemd_service("nginx")
    get_uptime_of_pm2_service("temporary value")


def get_uptime_of_systemd_service(service: str):
    unparsed_time = subprocess.run(
        ["/usr/bin/systemctl", "show", "--property=ActiveEnterTimestamp", service],
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8")
    list_of_time = unparsed_time.split("=")[-1].strip()
    date = datetime.strptime(
        list_of_time,
        "%a %Y-%m-%d %H:%M:%S %Z",
    )
    return date


def get_uptime_of_pm2_service(service: str):
    unparsed_time = json.loads(
        subprocess.run(
            [
                "pm2",
                "jlist",
            ],
            capture_output=True,
            check=True,
        ).stdout.decode("utf-8")
    )
    parsed_time = list(map(lambda x: x["pm2_env"]["env"], unparsed_time))
    print(parsed_time)


if __name__ == "__main__":
    main()
