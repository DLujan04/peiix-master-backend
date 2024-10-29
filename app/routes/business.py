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
            'Authorization': token
        }
        
        logger.debug(f"Headers a enviar a la API: {headers}")
        
        response = requests.get(
            'http://ec2-107-20-101-226.compute-1.amazonaws.com/sociedades',
            headers=headers
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
            'Authorization': token
        }
        
        logger.debug(f"Headers a enviar a la API: {headers}")
        
        response = requests.get(
            'http://ec2-107-20-101-226.compute-1.amazonaws.com/giros',
            headers=headers
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
