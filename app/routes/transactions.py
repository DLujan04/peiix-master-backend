from flask import Blueprint, request, jsonify, current_app, send_file, render_template_string
import requests
import logging
import csv
import io
from weasyprint import HTML
from functools import wraps
from datetime import datetime
import math
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

@transactions_blueprint.route('/export', methods=['GET'])
@token_required
def export_transactions():
    try:
        # Validar parámetros requeridos
        date_from = request.args.get('dateFrom')
        date_to = request.args.get('dateTo')
        export_format = request.args.get('format', 'csv').lower()

        if not date_from or not date_to:
            logger.error("Faltan parámetros requeridos dateFrom y/o dateTo")
            return jsonify({'error': 'dateFrom and dateTo are required'}), 400

        if export_format not in ['csv', 'pdf']:
            logger.error("Formato de exportación inválido")
            return jsonify({'error': 'Format must be either csv or pdf'}), 400

        # Obtener parámetros opcionales
        size = request.args.get('size', type=int, default=100)  # Tamaño por página
        page = request.args.get('page', type=int, default=1)    # Página inicial (1-based indexing)
        device = request.args.get('device')
        bin_number = request.args.get('bin')
        capture_method = request.args.get('captureMethod')
        transaction_status = request.args.get('transactionStatus')
        transaction_type = request.args.get('transactionType')
        card = request.args.get('card')

        # Obtener tokens de los headers
        auth_header = request.headers.get('Authorization')
        logger.debug(f"Token en export_transactions: {auth_header}")

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

        all_transactions = []
        current_page = page

        while True:
            params['page'] = current_page
            response = requests.get(
                f"{api_base_url}/transactions",
                headers=headers,
                params=params,
                verify=False  # Considera usar True en producción
            )

            logger.debug(f"Respuesta de la API: Status {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Error al obtener transacciones: {response.text}")
                return jsonify({'error': 'Error al obtener transacciones', 'details': response.text}), response.status_code

            data = response.json()
            logger.debug(f"Respuesta completa de la API: {data}")  # Añadido para depuración

            transactions = data.get('data', [])
            logger.debug(f"Transacciones obtenidas en página {current_page}: {len(transactions)}")
            all_transactions.extend(transactions)

            total = data.get('total', 0)
            per_page = data.get('perPage', size)  # Usa 'perPage' de la respuesta o el valor enviado
            if per_page == 0:
                per_page = size  # Evita división por cero

            # Calcular el número total de páginas
            total_pages = math.ceil(total / per_page) if per_page else 1
            logger.debug(f"Páginas Totales: {total_pages}, Página Actual: {current_page}")

            if current_page >= total_pages:
                break
            current_page += 1

        logger.debug(f"Total de transacciones obtenidas: {len(all_transactions)}")

        if not all_transactions:
            return jsonify({'message': 'No se encontraron transacciones para exportar'}), 200

        # Generar nombre de archivo dinámico
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if export_format == 'csv':
            # Generar CSV
            proxy = io.StringIO()
            writer = csv.DictWriter(proxy, fieldnames=all_transactions[0].keys())
            writer.writeheader()
            writer.writerows(all_transactions)
            mem = io.BytesIO()
            mem.write(proxy.getvalue().encode('utf-8'))
            mem.seek(0)
            proxy.close()
            filename = f"transactions_{timestamp}.csv"
            return send_file(
                mem,
                as_attachment=True,
                download_name=filename,
                mimetype='text/csv'
            )

        elif export_format == 'pdf':
            # Definir las columnas importantes para el PDF
            # Según la interfaz proporcionada
            pdf_headers = ['transaction_id', 'total_amount', 'date', 'bank', 'transaction_status']

            # Verificar que las columnas existan en los datos
            available_headers = all_transactions[0].keys()
            pdf_headers = [header for header in pdf_headers if header in available_headers]
            logger.debug(f"Encabezados filtrados para PDF: {pdf_headers}")

            if not pdf_headers:
                logger.error("No se encontraron columnas válidas para el PDF.")
                return jsonify({'error': 'No se encontraron columnas válidas para el PDF.'}), 500

            # Definir la plantilla HTML usando Jinja2 con estilos ajustados
            html_template = """
            <html>
                <head>
                    <style>
                        @page { size: A4 landscape; margin: 10mm; }
                        body { font-family: Arial, sans-serif; font-size: 8pt; }
                        table { width: 100%; border-collapse: collapse; table-layout: fixed; word-wrap: break-word; }
                        th, td { border: 1px solid #dddddd; padding: 4px; text-align: left; }
                        th { background-color: #f2f2f2; font-size: 9pt; }
                        h2 { text-align: center; font-size: 14pt; }
                    </style>
                </head>
                <body>
                    <h2>Transacciones</h2>
                    <table>
                        <thead>
                            <tr>
                                {% for header in headers %}
                                    <th>{{ header.replace('_', ' ').capitalize() }}</th>
                                {% endfor %}
                            </tr>
                        </thead>
                        <tbody>
                            {% for txn in transactions %}
                                <tr>
                                    {% for header in headers %}
                                        <td>{{ txn[header] if txn[header] is not none else '' }}</td>
                                    {% endfor %}
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </body>
            </html>
            """

            # Renderizar la plantilla con las columnas filtradas
            html_content = render_template_string(
                html_template,
                headers=pdf_headers,
                transactions=all_transactions
            )

            logger.debug(f"Contenido HTML para PDF:\n{html_content}")

            # Verificar que el HTML no esté vacío
            if not html_content.strip():
                logger.error("El contenido HTML generado para el PDF está vacío.")
                return jsonify({'error': 'El contenido HTML para el PDF está vacío.'}), 500

            # Generar el PDF usando WeasyPrint
            try:
                pdf_file = HTML(string=html_content).write_pdf()
            except Exception as e:
                logger.error(f"Error al generar el PDF: {e}")
                return jsonify({'error': 'Error al generar el PDF', 'details': str(e)}), 500

            # Verificar que el PDF no esté vacío
            if not pdf_file:
                logger.error("El archivo PDF generado está vacío.")
                return jsonify({'error': 'El archivo PDF generado está vacío.'}), 500

            mem = io.BytesIO(pdf_file)
            mem.seek(0)
            filename = f"transactions_{timestamp}.pdf"
            return send_file(
                mem,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )

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
