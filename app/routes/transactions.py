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
            'Authorization': token,
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
        
        response = requests.get(
            'http://ec2-107-20-101-226.compute-1.amazonaws.com/transactions',
            headers=headers,
            params=params
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