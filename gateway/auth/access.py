import os, requests
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def login(req) -> tuple[str | None , tuple[str, int] | None]:
    auth = req.authorization
    if not auth:
        logger.error("Missing authorization header")
        return None, ("Missing authorization header", 401)

    basicauth = (auth.username, auth.password)
    auth_service_url = f"http://{os.environ.get('AUTH_SVC_ADDR')}/login"

    logger.info(f"Attempting to connect to auth service at: {auth_service_url}")
    logger.info(f"Username: {auth.username}")

    try:
        response = requests.post(
            auth_service_url,
            auth=basicauth,
            timeout=10
        )

        logger.info(f"Auth service response status: {response.status_code}")
        logger.info(f"Auth service response text: {response.text}")

        if response.status_code == 200:
            return response.text, None
        else:
            return None, (response.text, response.status_code)

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error to auth service: {e}")
        return None, ("Auth service unavailable", 503)
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout error to auth service: {e}")
        return None, ("Auth service timeout", 504)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None, ("Internal server error", 500)
