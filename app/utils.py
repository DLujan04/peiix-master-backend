from flask import request, jsonify, current_app
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Obtener el token del header Authorization
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Verificar si el token viene con el prefijo "Bearer"
            if ' ' in auth_header:
                scheme, token = auth_header.split(' ', 1)
                if scheme.lower() != 'bearer':
                    return jsonify({'message': 'Invalid token format'}), 401
            else:
                token = auth_header
            
            # Actualizar el token en la configuración de la app
            current_app.config['ACCESS_TOKEN'] = token
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': f'Invalid token: {str(e)}'}), 401
    
    return decorated