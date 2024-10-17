from flask import Blueprint

authorization_blueprint = Blueprint('authorization', __name__)

@authorization_blueprint.route('/login', methods=['POST'])
def login():
    # Aquí irá la lógica de inicio de sesión
    return "Login route"
