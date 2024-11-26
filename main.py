from flask import Flask
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Crear instancia de Flask
app = Flask(__name__)

# Configurar el puerto (5000 por defecto)
PORT = int(os.getenv("PORT", 5000))

# Cargar tokens y URL base en la configuración de Flask
app.config['ACCESS_TOKEN'] = os.getenv("ACCESS_TOKEN")
app.config['BP_TOKEN'] = os.getenv("BP_TOKEN")
app.config['REFRESH_TOKEN'] = os.getenv("REFRESH_TOKEN")
app.config['USER_TOKEN'] = os.getenv("USER_TOKEN")
app.config['BASE_API_URL'] = os.getenv("BASE_API_URL")  # URL de la API
app.config['ENCRYPTION_KEY'] = os.getenv("ENCRYPTION_KEY") 

# Importar y registrar los blueprints
from app.routes.authorization import authorization_blueprint
from app.routes.transactions import transactions_blueprint

#test
app.register_blueprint(authorization_blueprint)
app.register_blueprint(transactions_blueprint)

@app.route('/')
def home():
    return "Backend de Peiix Master funcionando"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT, debug=True)
