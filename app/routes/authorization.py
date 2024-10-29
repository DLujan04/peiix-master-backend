from flask import Blueprint, request, jsonify, current_app
import requests
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

authorization_blueprint = Blueprint('authorization', __name__)

@authorization_blueprint.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        logger.debug("Datos de login recibidos")
        
        if not data or 'username' not in data or 'password' not in data:
            logger.error("Faltan credenciales de login")
            return jsonify({'error': 'Missing username or password'}), 400
        
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(
            'http://ec2-107-20-101-226.compute-1.amazonaws.com/login',
            json={
                'username': data['username'],
                'password': data['password']
            },
            headers=headers
        )
        
        logger.debug(f"Respuesta del login: Status {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            # Actualizar los tokens en la configuración de la app
            current_app.config['ACCESS_TOKEN'] = response_data.get('access_token')
            current_app.config['BP_TOKEN'] = response_data.get('bp_token')
            current_app.config['REFRESH_TOKEN'] = response_data.get('refresh_token')
            current_app.config['USER_TOKEN'] = response_data.get('user_token')
            
            logger.debug("Tokens actualizados en la configuración de la app")
            
            # Actualizar el archivo .env
            try:
                with open('.env', 'w') as f:
                    f.write(f"ACCESS_TOKEN={response_data.get('access_token')}\n")
                    f.write(f"BP_TOKEN={response_data.get('bp_token')}\n")
                    f.write(f"REFRESH_TOKEN={response_data.get('refresh_token')}\n")
                    f.write(f"USER_TOKEN={response_data.get('user_token')}\n")
                logger.debug("Tokens actualizados en archivo .env")
            except Exception as e:
                logger.error(f"Error actualizando .env: {str(e)}")
        
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
        
        response = requests.post(
            'http://ec2-107-20-101-226.compute-1.amazonaws.com/refresh',
            json={'refresh_token': data['refresh_token']},
            headers=headers
        )
        
        logger.debug(f"Respuesta del refresh: Status {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            # Actualizar los tokens en la configuración de la app
            current_app.config['ACCESS_TOKEN'] = response_data.get('access_token')
            current_app.config['BP_TOKEN'] = response_data.get('bp_token')
            current_app.config['REFRESH_TOKEN'] = response_data.get('refresh_token')
            current_app.config['USER_TOKEN'] = response_data.get('user_token')
            
            logger.debug("Tokens actualizados en la configuración de la app")
            
            # Actualizar el archivo .env
            try:
                with open('.env', 'w') as f:
                    f.write(f"ACCESS_TOKEN={response_data.get('access_token')}\n")
                    f.write(f"BP_TOKEN={response_data.get('bp_token')}\n")
                    f.write(f"REFRESH_TOKEN={response_data.get('refresh_token')}\n")
                    f.write(f"USER_TOKEN={response_data.get('user_token')}\n")
                logger.debug("Tokens actualizados en archivo .env")
            except Exception as e:
                logger.error(f"Error actualizando .env: {str(e)}")
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        logger.error(f"Error en refresh: {str(e)}")
        return jsonify({'error': str(e)}), 500