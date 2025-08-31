import jwt, datetime, os
from flask import Flask, request, jsonify, Response
from flask_mysqldb import MySQL

# ===================================================================================================
# Configurations
# ===================================================================================================
app = Flask(__name__)
mysql = MySQL(app)

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'demo_user')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'secure_password')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'some_db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')


# ===================================================================================================
# Routes
#   - POST  /login      {Basic Authorization}
#   - GET   /me         {Bearer Authorization}
#   - GET   /health     NONE
# ===================================================================================================
@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return Response('Please provide proper authorization headers', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if not hasattr(mysql, 'connection') or mysql.connection is None:
        return Response('Database connection error', 500)

    cursor = mysql.connection.cursor()
    res = cursor.execute("SELECT * FROM users WHERE email=%s", (auth.username,))

    if res > 0:
        user_row = cursor.fetchone()
        email, password =  user_row[1], user_row[2]

        if auth.username != email or auth.password != password:
            cursor.close()
            return Response('Email or password is incorrect', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
        else:
            token = create_token(email, app.config['SECRET_KEY'], True)
            cursor.close()
            return token
    else:
        cursor.close()
        return Response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

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
    return jsonify({'status': 'OK'})

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
