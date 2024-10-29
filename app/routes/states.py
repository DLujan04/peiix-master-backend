from flask import Blueprint, jsonify, current_app, request
import requests
import logging
from ..utils import token_required

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

states_blueprint = Blueprint('states', __name__)

@states_blueprint.route('/estados', methods=['GET'])
@token_required
def get_estados():
    try:
        # Obtener el token del header de la request
        auth_header = request.headers.get('Authorization')
        logger.debug(f"Token recibido en /estados: {auth_header}")

        headers = {
            'Authorization': auth_header,  
        }
        
        logger.debug(f"Headers enviados a la API: {headers}")

        response = requests.get(
            'http://ec2-107-20-101-226.compute-1.amazonaws.com/estados',
            headers=headers
        )
        
        logger.debug(f"Código de estado de la respuesta: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Error en la respuesta: {response.text}")
            return jsonify({
                'error': 'Error en la petición a la API',
                'status_code': response.status_code,
                'details': response.text
            }), response.status_code

        return response.text, response.status_code, {'Content-Type': 'application/json'}

    except requests.RequestException as e:
        logger.error(f"Error en la petición HTTP: {str(e)}")
        return jsonify({
            'error': 'Error de conexión con la API',
            'details': str(e)
        }), 500
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@states_blueprint.route('/estados/<id_estado>', methods=['GET'])
@token_required
def get_municipios(id_estado):
    try:
        # Obtener el token del header de la request
        auth_header = request.headers.get('Authorization')
        logger.debug(f"Token recibido en /estados/{id_estado}: {auth_header}")

        headers = {
            'Authorization': auth_header,  
        }
        
        logger.debug(f"Headers enviados a la API: {headers}")

        response = requests.get(
            f'http://ec2-107-20-101-226.compute-1.amazonaws.com/estados/{id_estado}',
            headers=headers
        )
        
        logger.debug(f"Código de estado de la respuesta: {response.status_code}")

        if response.status_code != 200:
            logger.error(f"Error en la respuesta: {response.text}")
            return jsonify({
                'error': 'Error en la petición a la API',
                'status_code': response.status_code,
                'details': response.text
            }), response.status_code

        return jsonify(response.json()), response.status_code

    except requests.RequestException as e:
        logger.error(f"Error en la petición HTTP: {str(e)}")
        return jsonify({
            'error': 'Error de conexión con la API',
            'details': str(e)
        }), 500
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500