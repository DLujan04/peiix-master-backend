from flask import Blueprint, jsonify, request, current_app
import requests
import logging
from ..utils import token_required

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

business_blueprint = Blueprint('business', __name__)

@business_blueprint.route('/sociedades', methods=['GET'])
@token_required
def get_sociedades():
    try:
        auth_header = request.headers.get('Authorization')
        logger.debug(f"Token en get_sociedades: {auth_header}")
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = auth_header
            
        headers = {
            'Authorization': f"Bearer {token}"
        }
        
        logger.debug(f"Headers a enviar a la API: {headers}")
        
        # Usar URL base desde la configuración
        api_base_url = current_app.config.get('BASE_API_URL')
        if not api_base_url:
            raise ValueError("BASE_API_URL no está configurado en el servidor.")

        response = requests.get(
            f"{api_base_url}/sociedades",
            headers=headers,
            verify=False
        )
        
        logger.debug(f"Respuesta de la API: Status {response.status_code}")
        logger.debug(f"Respuesta body: {response.text[:200]}...")
        
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

@business_blueprint.route('/giros', methods=['GET'])
@token_required
def get_giros():
    try:
        auth_header = request.headers.get('Authorization')
        logger.debug(f"Token en get_giros: {auth_header}")
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = auth_header
            
        headers = {
            'Authorization': f"Bearer {token}"
        }
        
        logger.debug(f"Headers a enviar a la API: {headers}")
        
        # Usar URL base desde la configuración
        api_base_url = current_app.config.get('BASE_API_URL')
        if not api_base_url:
            raise ValueError("BASE_API_URL no está configurado en el servidor.")

        response = requests.get(
            f"{api_base_url}/giros",
            headers=headers,
            verify=False
        )
        
        logger.debug(f"Respuesta de la API: Status {response.status_code}")
        logger.debug(f"Respuesta body: {response.text[:200]}...")
        
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
