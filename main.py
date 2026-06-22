import subprocess
from datetime import datetime
import json

from fastapi import FastAPI, HTTPException

app = FastAPI(title="LRIMa Status Validation API")

SERVICE_WHITELIST: dict[str, str] = {
    "nginx": "systemd",
    "culture-backend": "pm2",
    "disease-detection": "pm2",
    "server": "pm2",
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
    index_of_service = names.index(service)
    uptimes = [x["pm2_env"]["pm_uptime"] for x in unparsed_time]
    return datetime.fromtimestamp(uptimes[index_of_service] / 1000)


@app.get("/uptime/{service_name}")
def get_service_uptime(service_name: str):
    manager = SERVICE_WHITELIST.get(service_name)
    if manager is None:
        raise HTTPException(
            status_code=403,
            detail=f"Service '{service_name}' is not in the whitelist.",
        )

    match manager:
        case "systemd":
            uptime = get_uptime_of_systemd_service(service_name)
        case "pm2":
            uptime = get_uptime_of_pm2_service(service_name)
        case _:
            raise HTTPException(status_code=500, detail=f"Unknown manager: {manager}")

    return {
        "service": service_name,
        "manager": manager,
        "uptime": uptime.isoformat(),
    }


@app.get("/uptime/")
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
                raise HTTPException(
                    status_code=500, detail=f"Unknown manager: {manager}"
                )
        all_times.append(
            {
                "service": i,
                "uptime": uptime.isoformat(),
            }
        )

    return
