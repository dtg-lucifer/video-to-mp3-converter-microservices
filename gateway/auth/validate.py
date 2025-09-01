import os
from flask import Request
import requests

def token(request: Request) -> tuple[str | None, tuple[str | None, int] | None]:
    if 'Authorization' not in request.headers:
        return None, ("Authorization header missing", 401)

    auth_header = request.headers['Authorization']
    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None, ("Invalid Authorization header format", 401)

    token = parts[1]

    if not token:
        return None, ("Token is missing", 401)

    response = requests.get(
        f"http://{os.environ.get('AUTH_SVC_ADDR')}/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
