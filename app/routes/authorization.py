from flask import Blueprint, request, jsonify, current_app
import requests
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

authorization_blueprint = Blueprint('authorization', __name__)

def update_env_tokens(new_tokens):
    # Leer el archivo .env y guardar su contenido existente
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as file:
            for line in file:
                key, sep, value = line.partition("=")
                env_vars[key.strip()] = value.strip()

    # Actualizar las variables de entorno con los nuevos tokens
    env_vars.update({
        "ACCESS_TOKEN": new_tokens.get('access_token', ''),
        "BP_TOKEN": new_tokens.get('bp_token', ''),
        "REFRESH_TOKEN": new_tokens.get('refresh_token', ''),
        "USER_TOKEN": new_tokens.get('user_token', ''),
    })

    # Escribir todas las variables de entorno de nuevo en el archivo
    with open('.env', 'w') as file:
        for key, value in env_vars.items():
            file.write(f"{key}={value}\n")

@authorization_blueprint.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        logger.debug("Datos de login recibidos")
        
        if not data or 'username' not in data or 'password' not in data:
            logger.error("Faltan credenciales de login")
            return jsonify({'error': 'Missing username or password'}), 400
        
        headers = {'Content-Type': 'application/json'}
        
        # Usar URL base desde la configuración
        api_base_url = current_app.config.get('BASE_API_URL')
        response = requests.post(
            f"{api_base_url}/login",
            json={'username': data['username'], 'password': data['password']},
            headers=headers,
            verify=False
        )
        
        logger.debug(f"Respuesta del login: Status {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Actualizar los tokens en la configuración de la app
            current_app.config['ACCESS_TOKEN'] = response_data.get('access_token')
            current_app.config['BP_TOKEN'] = response_data.get('bp_token')
            current_app.config['REFRESH_TOKEN'] = response_data.get('refresh_token')
            current_app.config['USER_TOKEN'] = response_data.get('user_token')
            
            # Actualizar el archivo .env solo con los tokens, sin borrar el resto del contenido
            update_env_tokens(response_data)
            logger.debug("Tokens actualizados en archivo .env")
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        return jsonify({'error': str(e)}), 500

@authorization_blueprint.route('/refresh', methods=['POST'])
def refresh_token():
    try:
        data = request.get_json()
        logger.debug("Solicitud de refresh token recibida")
        
        if not data or 'refresh_token' not in data:
            logger.error("Falta refresh_token en la solicitud")
            return jsonify({'error': 'Missing refresh token'}), 400
        
        headers = {'Content-Type': 'application/json'}
        
        # Usar URL base desde la configuración
        api_base_url = current_app.config.get('BASE_API_URL')
        response = requests.post(
            f"{api_base_url}/refresh",
            json={'refresh_token': data['refresh_token']},
            headers=headers,
            verify=False
        )
        
        logger.debug(f"Respuesta del refresh: Status {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            current_app.config['ACCESS_TOKEN'] = response_data.get('access_token')
            current_app.config['BP_TOKEN'] = response_data.get('bp_token')
            current_app.config['REFRESH_TOKEN'] = response_data.get('refresh_token')
            current_app.config['USER_TOKEN'] = response_data.get('user_token')
            
            # Actualizar el archivo .env solo con los tokens, sin borrar el resto del contenido
            update_env_tokens(response_data)
            logger.debug("Tokens actualizados en archivo .env")
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        logger.error(f"Error en refresh: {str(e)}")
        return jsonify({'error': str(e)}), 500
