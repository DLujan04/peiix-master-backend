from flask import Flask
from dotenv import load_dotenv
from routes.routes import routes_blueprint  
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Crea la instancia de Flask
app = Flask(__name__)

# Configurar el puerto desde las variables de entorno o usar 5000 por defecto
PORT = int(os.getenv("PORT", 5000))

# Registrar el blueprint después de crear la instancia Flask
app.register_blueprint(routes_blueprint)

@app.route('/')
def home():
    return "Backend de Peiix Master funcionando"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
