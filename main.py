import subprocess
from datetime import datetime
import json

from flask import Flask, jsonify, abort

app = Flask(__name__)

SERVICE_WHITELIST: dict[str, str] = {
    "nginx": "systemd",
    "LRIMaCulture Disease Detection": "pm2",
    "LRIMaCulture Imager": "pm2",
    "LRIMaCulture Backend": "pm2",
    "LRIMaCulture Mobile Application": "pm2",
}


def get_uptime_of_systemd_service(service: str) -> datetime:
    unparsed_time = subprocess.run(
        ["/usr/bin/systemctl", "show", "--property=ActiveEnterTimestamp", service],
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8")
    list_of_time = unparsed_time.split("=")[-1].strip()
    return datetime.strptime(list_of_time, "%a %Y-%m-%d %H:%M:%S %Z")


def get_uptime_of_pm2_service(service: str) -> datetime:
    unparsed_time = json.loads(
        subprocess.run(
            ["pm2", "jlist"],
            capture_output=True,
            check=True,
        ).stdout.decode("utf-8")
    )
    names = [x["name"] for x in unparsed_time]
    is_alive = [True if x["pid"] != 0 else False for x in unparsed_time]
    index_of_service = names.index(service)
    uptimes = [x["pm2_env"]["pm_uptime"] for x in unparsed_time]
    return datetime.fromtimestamp(
        uptimes[index_of_service] / 1000 if is_alive[index_of_service] else 0
    )


@app.route("/uptime/<service_name>")
def get_service_uptime(service_name: str):
    manager = SERVICE_WHITELIST.get(service_name)
    if manager is None:
        abort(403, description=f"Service '{service_name}' is not in the whitelist.")

    match manager:
        case "systemd":
            uptime = get_uptime_of_systemd_service(service_name)
        case "pm2":
            uptime = get_uptime_of_pm2_service(service_name)
        case _:
            abort(500, description=f"Unknown manager: {manager}")

    return jsonify(
        {
            "service": service_name,
            "manager": manager,
            "uptime": uptime.isoformat(),
        }
    )


@app.route("/uptime")
def get_service_uptime_all():
    all_times = []
    for i in SERVICE_WHITELIST:
        manager = SERVICE_WHITELIST.get(i)

        uptime = None
        match manager:
            case "systemd":
                uptime = get_uptime_of_systemd_service(i)
            case "pm2":
                uptime = get_uptime_of_pm2_service(i)
            case _:
                abort(500, description=f"Unknown manager: {manager}")
        all_times.append(
            {
                "service": i,
                "uptime": uptime.isoformat(),
            }
        )

    return jsonify(all_times)
