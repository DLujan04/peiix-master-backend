from flask import Blueprint

routes_blueprint = Blueprint('routes', __name__)

@routes_blueprint.route('/')
def home():
    return "Hello, World!"