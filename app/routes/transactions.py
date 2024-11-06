from flask import Blueprint, jsonify, request, current_app
import requests
import logging
from ..utils import token_required

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

transactions_blueprint = Blueprint('transactions', __name__)

@transactions_blueprint.route('/transactions', methods=['GET'])
@token_required
def get_transactions():
    try:
        # Validar parámetros requeridos
        date_from = request.args.get('dateFrom')
        date_to = request.args.get('dateTo')
        
        if not date_from or not date_to:
            logger.error("Faltan parámetros requeridos dateFrom y/o dateTo")
            return jsonify({'error': 'dateFrom and dateTo are required'}), 400
        
        # Obtener parámetros opcionales
        size = request.args.get('size')
        page = request.args.get('page')
        device = request.args.get('device')
        bin_number = request.args.get('bin')
        capture_method = request.args.get('captureMethod')
        transaction_status = request.args.get('transactionStatus')
        transaction_type = request.args.get('transactionType')
        card = request.args.get('card')
        
        # Obtener tokens de los headers
        auth_header = request.headers.get('Authorization')
        logger.debug(f"Token en get_transactions: {auth_header}")
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = auth_header
        
        headers = {
            'Authorization': f"Bearer {token}",
            'bp-token': current_app.config['BP_TOKEN']
        }
        
        logger.debug(f"Headers a enviar a la API: {headers}")
        
        params = {
            'dateFrom': date_from,
            'dateTo': date_to,
            'size': size,
            'page': page,
            'device': device,
            'bin': bin_number,
            'captureMethod': capture_method,
            'transactionStatus': transaction_status,
            'transactionType': transaction_type,
            'card': card
        }
        
        # Eliminar parámetros None
        params = {k: v for k, v in params.items() if v is not None}
        
        logger.debug(f"Parámetros de la petición: {params}")
        
        # Usar URL base desde la configuración
        api_base_url = current_app.config.get('BASE_API_URL')
        if not api_base_url:
            raise ValueError("BASE_API_URL no está configurado en el servidor.")

        response = requests.get(
            f"{api_base_url}/transactions",
            headers=headers,
            params=params,
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

@transactions_blueprint.route('/estados', methods=['GET'])
@token_required
def get_estados():
    try:
        # Obtener el token del header de la request
        auth_header = request.headers.get('Authorization')
        logger.debug(f"Token recibido en /estados: {auth_header}")

        headers = {
            'Authorization': auth_header,  
        }
        
        # Usar URL base desde la configuración
        api_base_url = current_app.config.get('BASE_API_URL')
        if not api_base_url:
            raise ValueError("BASE_API_URL no está configurado en el servidor.")
        
        response = requests.get(
            f"{api_base_url}/estados",
            headers=headers,
            verify=False
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

@transactions_blueprint.route('/estados/<id_estado>', methods=['GET'])
@token_required
def get_municipios(id_estado):
    try:
        # Obtener el token del header de la request
        auth_header = request.headers.get('Authorization')
        logger.debug(f"Token recibido en /estados/{id_estado}: {auth_header}")

        headers = {
            'Authorization': auth_header,  
        }
        
        # Usar URL base desde la configuración
        api_base_url = current_app.config.get('BASE_API_URL')
        if not api_base_url:
            raise ValueError("BASE_API_URL no está configurado en el servidor.")

        response = requests.get(
            f"{api_base_url}/estados/{id_estado}",
            headers=headers,
            verify=False
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


@transactions_blueprint.route('/sociedades', methods=['GET'])
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

@transactions_blueprint.route('/giros', methods=['GET'])
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
