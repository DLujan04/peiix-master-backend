from flask import Blueprint, jsonify, request, current_app, send_file
import requests
import logging
import random
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from ..utils import token_required

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

transactions_blueprint = Blueprint('transactions', __name__, url_prefix='/transactions')

def export_to_csv(transactions):
    df = pd.DataFrame(transactions)
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output

def export_to_pdf(transactions):
    output = BytesIO()
    pdf_canvas = canvas.Canvas(output, pagesize=letter)
    width, height = letter
    pdf_canvas.setFont("Helvetica", 10)
    
    y_position = height - 50
    line_height = 15

    for transaction in transactions:
        for key, value in transaction.items():
            pdf_canvas.drawString(50, y_position, f"{key}: {value}")
            y_position -= line_height
            if y_position < 50:
                pdf_canvas.showPage()
                pdf_canvas.setFont("Helvetica", 10)
                y_position = height - 50
        y_position -= line_height

    pdf_canvas.save()
    output.seek(0)
    return output

def fetch_additional_data(headers):
    """Obtiene datos de /estados, /giros, /sociedades y los almacena en un diccionario."""
    api_base_url = current_app.config.get('BASE_API_URL')
    additional_data = {}

    # Llamada al endpoint /estados
    estados_response = requests.get(f"{api_base_url}/estados", headers=headers, verify=False)
    if estados_response.status_code == 200:
        additional_data['estados'] = estados_response.json()
    else:
        logger.error("Error al obtener datos de /estados")

    # Llamada al endpoint /giros
    giros_response = requests.get(f"{api_base_url}/giros", headers=headers, verify=False)
    if giros_response.status_code == 200:
        additional_data['giros'] = giros_response.json()
    else:
        logger.error("Error al obtener datos de /giros")

    # Llamada al endpoint /sociedades
    sociedades_response = requests.get(f"{api_base_url}/sociedades", headers=headers, verify=False)
    if sociedades_response.status_code == 200:
        additional_data['sociedades'] = sociedades_response.json()
    else:
        logger.error("Error al obtener datos de /sociedades")

    return additional_data

def fetch_municipios_for_estado(headers, estado_id):
    """Obtiene datos de municipios de un estado específico."""
    api_base_url = current_app.config.get('BASE_API_URL')
    municipios_response = requests.get(f"{api_base_url}/estados/{estado_id}", headers=headers, verify=False)
    if municipios_response.status_code == 200:
        return municipios_response.json()
    else:
        logger.error(f"Error al obtener municipios para el estado {estado_id}")
        return None

@transactions_blueprint.route('/', methods=['GET'])
@token_required
def get_transactions():
    try:
        # Configuración de parámetros de fecha obligatorios
        date_from = request.args.get('dateFrom')
        date_to = request.args.get('dateTo')
        
        if not date_from or not date_to:
            logger.error("Faltan parámetros requeridos dateFrom y/o dateTo")
            return jsonify({'error': 'dateFrom and dateTo are required'}), 400
        
        # Parámetros de paginación
        size = int(request.args.get('size', 10))  # Número de transacciones por página (10 por defecto)
        page = int(request.args.get('page', 1))   # Página solicitada (1 por defecto)
        export_format = request.args.get('format', 'json').lower()

        # Otros filtros opcionales
        device = request.args.get('device')
        bin_number = request.args.get('bin')
        capture_method = request.args.get('captureMethod')
        transaction_status = request.args.get('transactionStatus')
        transaction_type = request.args.get('transactionType')
        card = request.args.get('card')

        # Obtener el token de autorización
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1] if 'Bearer ' in auth_header else auth_header
        
        headers = {
            'Authorization': f"Bearer {token}",
            'bp-token': current_app.config['BP_TOKEN']
        }
        
        # Parámetros para la solicitud de transacciones
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
        
        # Filtra parámetros nulos
        params = {k: v for k, v in params.items() if v is not None}
        
        api_base_url = current_app.config.get('BASE_API_URL')
        if not api_base_url:
            raise ValueError("BASE_API_URL no está configurado en el servidor.")

        # Obtener las transacciones desde la API externa
        response = requests.get(
            f"{api_base_url}/transactions",
            headers=headers,
            params=params,
            verify=False
        )

        if response.status_code != 200:
            return jsonify({'error': 'Error en la API', 'details': response.text}), response.status_code

        # Extraer datos de transacciones y total de elementos para la paginación
        response_data = response.json()
        if 'data' not in response_data:
            logger.error("Formato inesperado de datos en la respuesta de la API")
            return jsonify({'error': 'Formato inesperado de datos en la respuesta de la API'}), 500
        
        transactions = response_data['data']
        total_items = response_data.get('total', 0)  # Total de transacciones
        total_pages = (total_items + size - 1) // size  # Calcula el total de páginas

        # Obtener datos adicionales de /estados, /giros, /sociedades
        additional_data = fetch_additional_data(headers)

        # Añadir datos aleatorios de /estados, /municipios, /giros y /sociedades a cada transacción
        for transaction in transactions:
            estado = random.choice(additional_data.get('estados', []))
            transaction['estado'] = estado  # Asignar un estado aleatorio

            if estado and 'id' in estado:
                # Obtener un municipio aleatorio para el estado seleccionado
                municipios = fetch_municipios_for_estado(headers, estado['id'])
                if municipios:
                    transaction['municipio'] = random.choice(municipios)

            transaction['giro'] = random.choice(additional_data.get('giros', [])) if additional_data.get('giros') else None
            transaction['sociedad'] = random.choice(additional_data.get('sociedades', [])) if additional_data.get('sociedades') else None

        # Estructura de respuesta con paginación
        response_with_pagination = {
            'data': transactions,
            'currentPage': page,
            'totalPages': total_pages,
            'totalItems': total_items,
            'pageSize': size
        }

        # Exportar el archivo en el formato solicitado
        if export_format == 'csv':
            output = export_to_csv(transactions)
            return send_file(output, mimetype='text/csv', as_attachment=True, download_name=f"transactions_page_{page}.csv")
        elif export_format == 'pdf':
            output = export_to_pdf(transactions)
            return send_file(output, mimetype='application/pdf', as_attachment=True, download_name=f"transactions_page_{page}.pdf")
        else:
            return jsonify(response_with_pagination), 200

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
