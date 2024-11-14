from flask import Blueprint, request, jsonify, current_app
import requests
import logging
import os
import json
from cryptography.fernet import Fernet

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Definir el blueprint
authorization_blueprint = Blueprint('authorization', __name__)

def update_env_tokens(new_tokens):
    """
    Actualiza las variables de entorno en el archivo .env con los nuevos tokens.
    Solo actualiza las variables especificadas sin borrar el resto del contenido.
    """
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

# Cargar la clave de encriptación desde una variable de entorno
encryption_key = os.environ.get('ENCRYPTION_KEY')
if not encryption_key:
    logger.error("No se encontró la clave de encriptación en la configuración.")
    raise ValueError("No se encontró la clave de encriptación en la configuración.")

# Inicializar Fernet con la clave
fernet = Fernet(encryption_key.encode())

@authorization_blueprint.route('/login', methods=['POST'])
def login():
    """
    Endpoint para manejar el login de usuarios.
    - Encripta la contraseña recibida.
    - Envía las credenciales al API externo.
    - Actualiza los tokens si el login es exitoso.
    - Guarda las credenciales encriptadas en fernet.txt como JSON.
    - Verifica si el usuario ya existe antes de agregarlo.
    - Retorna la respuesta original del API externo.
    """
    try:
        data = request.get_json()
        logger.debug("Datos de login recibidos")

        # Validar la presencia de username y password
        if not data or 'username' not in data or 'password' not in data:
            logger.error("Faltan credenciales de login")
            return jsonify({'error': 'Missing username or password'}), 400

        username = data['username']
        password = data['password']

        # Encriptar la contraseña
        encrypted_password = fernet.encrypt(password.encode()).decode()
        logger.debug("Contraseña encriptada exitosamente")

        headers = {'Content-Type': 'application/json'}

        # Usar URL base desde la configuración
        api_base_url = current_app.config.get('BASE_API_URL')
        response = requests.post(
            f"{api_base_url}/login",
            json={'username': username, 'password': password},  # Enviando la contraseña original al API
            headers=headers,
            verify=False  # Como solicitaste, no modificaré esto
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

            # Guardar las credenciales encriptadas en fernet.txt como JSON, verificando si ya existe
            credenciales = {}
            archivo_path = 'fernet.txt'

            if os.path.exists(archivo_path):
                with open(archivo_path, 'r') as file:
                    try:
                        credenciales = json.load(file)
                        logger.debug("fernet.txt cargado exitosamente")
                    except json.JSONDecodeError:
                        logger.warning("fernet.txt no contiene JSON válido. Se creará uno nuevo.")
                        credenciales = {}
            else:
                logger.debug("fernet.txt no existe. Se creará uno nuevo.")

            # Verificar si el usuario ya existe
            if username not in credenciales:
                credenciales[username] = encrypted_password
                with open(archivo_path, 'w') as file:
                    json.dump(credenciales, file, indent=4)
                logger.debug(f"Credenciales del usuario '{username}' guardadas en fernet.txt")
            else:
                logger.debug(f"El usuario '{username}' ya existe en fernet.txt. No se agregará de nuevo.")

        # Retornar la respuesta original del API externo
        return jsonify(response.json()), response.status_code

    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        return jsonify({'error': str(e)}), 500

@authorization_blueprint.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Endpoint para manejar la renovación de tokens.
    - Envía el refresh_token al API externo.
    - Actualiza los tokens si la solicitud es exitosa.
    - Retorna la respuesta original del API externo.
    """
    try:
        data = request.get_json()
        logger.debug("Solicitud de refresh token recibida")

        # Validar la presencia de refresh_token
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
            verify=False  # Como solicitaste, no modificaré esto
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

        # Retornar la respuesta original del API externo
        return jsonify(response.json()), response.status_code

    except Exception as e:
        logger.error(f"Error en refresh: {str(e)}")
        return jsonify({'error': str(e)}), 500
