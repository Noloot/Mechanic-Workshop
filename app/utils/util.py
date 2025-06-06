from datetime import datetime, timedelta, timezone
from jose import jwt
import jose
from functools import wraps
from flask import request, jsonify
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or "a super secret, secret key"

def encode_token(user_id, role):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(user_id),
        'role': role
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token
    
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split(" ")
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
            
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user_id = int(data['sub'])
            request.user_role = data['role']
            
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
            return jsonify({'message': 'Invalid token!'}), 401
        
        return f(*args, **kwargs)

    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
            
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['sub']
            role = data['role']
            
            if role != 'mechanic':
                return jsonify({'message': 'Unauthorized: Mechanic role required'}), 403
            
            request.employee_id = user_id
            
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
            return jsonify({'message': 'Invalid token!'}), 401
        
        return f(*args, **kwargs)
    
    return decorated