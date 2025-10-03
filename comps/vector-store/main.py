import socket
import subprocess
import time
import threading
from typing import Dict, Any

from fastapi import FastAPI, HTTPException

app = FastAPI()

instances: Dict[str, Dict[str, Any]] = {}
DEFAULT_TTL = 600


def get_free_port():
    """Find an available port on the host machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def cleanup_worker():
    """Background worker to cleanup expired containers."""
    while True:
        now = time.time()
        expired_users = []
        for user, info in list(instances.items()):
            if info["expiry"] < now:
                expired_users.append(user)
        for user in expired_users:
            try:
                subprocess.run(["docker", "rm", "-f", f"qdrant_{user}"], check=False)
                del instances[user]
                print(f"[CLEANUP] Removed expired container for user {user}")
            except Exception as e:
                print(f"[CLEANUP ERROR] {e}")
        time.sleep(30)


threading.Thread(target=cleanup_worker, daemon=True).start()


@app.post("/create_instance")
def create_instance(user: str):
    now = time.time()

    if user in instances:
        info = instances[user]
        remaining = max(0, int(info["expiry"] - now))
        return {
            "message": f"Instance already exists for {user}",
            "user": user,
            "ip": "127.0.0.1",
            "port": info["port"],
            "ttl": remaining
        }

    port = get_free_port()
    container_name = f"qdrant_{user}"
    try:
        subprocess.run([
            "docker", "run", "-d",
            "--name", container_name,
            "-p", f"{port}:6333",
            "qdrant/qdrant"
        ], check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to start container: {e}")

    expiry = now + DEFAULT_TTL
    instances[user] = {"port": port, "expiry": expiry}

    return {
        "user": user,
        "ip": "127.0.0.1",
        "port": port,
        "ttl": DEFAULT_TTL
    }