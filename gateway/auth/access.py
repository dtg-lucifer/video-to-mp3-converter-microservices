import os, requests

def login(req) -> tuple[str | None , tuple[str, int] | None]:
    auth = req.authorization
    if not auth:
        return None, ("Missing authorization header", 401)

    basicauth = (auth.username, auth.password)
    response = requests.post(
        f"http://{os.environ.get("AUTH_SVC_ADDR")}/login",
        auth=basicauth
    )

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
