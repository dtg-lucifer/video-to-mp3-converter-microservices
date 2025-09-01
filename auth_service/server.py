import jwt, datetime, os, logging
from flask import Flask, request, jsonify, Response
from flask_mysqldb import MySQL

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ===================================================================================================
# Configurations
# ===================================================================================================
app = Flask(__name__)

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'demo_user')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'secure_password')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'auth_db')
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'your_secret_key')

mysql = MySQL(app)
# ===================================================================================================
# Routes
#   - POST  /login      {Basic Authorization}
#   - GET   /me         {Bearer Authorization}
#   - GET   /health     NONE
# ===================================================================================================
@app.route('/login', methods=['POST'])
def login():
    try:
        logger.info("Login attempt received")
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            logger.warning("Missing authorization headers")
            return Response('Please provide proper authorization headers', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

        logger.info(f"Login attempt for user: {auth.username}")

        if not hasattr(mysql, 'connection') or mysql.connection is None:
            logger.error("Database connection is None")
            return Response('Database connection error', 500)

        cursor = mysql.connection.cursor()
        logger.debug(f"Executing query for user: {auth.username}")
        res = cursor.execute("SELECT * FROM users WHERE email=%s", (auth.username,))
        logger.debug(f"Query returned {res} rows")

        if res > 0:
            user_row = cursor.fetchone()
            email, password = user_row[1], user_row[2]
            logger.debug(f"Found user: {email}")

            if auth.username != email or auth.password != password:
                logger.warning(f"Invalid credentials for user: {auth.username}")
                cursor.close()
                return Response('Email or password is incorrect', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
            else:
                logger.info(f"Creating token for user: {email}")
                token = create_token(email, app.config['SECRET_KEY'], True)
                cursor.close()
                logger.info("Login successful")
                return token
        else:
            logger.warning(f"User not found: {auth.username}")
            cursor.close()
            return Response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    except Exception as e:
        logger.error(f"Unexpected error in login: {e}")
        return Response('Internal server error', 500)

@app.route('/me', methods=['GET'])
def me():
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer'):
        return Response('Please provide proper authorization headers', 401, {'WWW-Authenticate': 'Bearer realm="Login required!"'})

    token = auth.split(' ')[1]
    decoded = validate_jwt(token, app.config['SECRET_KEY'])
    if decoded is None:
        return Response('Token is invalid or expired', 401, {'WWW-Authenticate': 'Bearer realm="Login required!"'})

    return decoded

@app.route('/health', methods=['GET'])
def health():
    try:
        # Test database connection
        if hasattr(mysql, 'connection') and mysql.connection is not None:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            db_status = "connected"
        else:
            db_status = "disconnected"
    except Exception as e:
        logger.error(f"Health check DB error: {e}")
        db_status = f"error: {str(e)}"

    return jsonify({
        'status': 'OK',
        'database': db_status,
        'mysql_host': app.config['MYSQL_HOST'],
        'mysql_user': app.config['MYSQL_USER'],
        'mysql_db': app.config['MYSQL_DB']
    })

# ===================================================================================================
# Helper methods
# ===================================================================================================
def create_token(username: str, secret: str, is_admin: bool) -> str:
    return jwt.encode(
        {
            'user_email': username,
            'is_admin': is_admin,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1),
            'iat': datetime.datetime.now(datetime.timezone.utc)
        },
        secret,
        algorithm='HS256'
    )

def validate_jwt(token: str, secret: str) -> dict | None:
    try:
        decoded = jwt.decode(token, secret, algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
