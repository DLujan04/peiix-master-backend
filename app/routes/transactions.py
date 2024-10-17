from flask import Blueprint

transactions_blueprint = Blueprint('transactions', __name__)

@transactions_blueprint.route('/transactions', methods=['GET'])
def get_transactions():
    # Aquí irá la lógica de mostrar transacciones
    return "Transactions route"
