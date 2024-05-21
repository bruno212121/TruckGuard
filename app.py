from app import create_app
import os 
from dotenv import load_dotenv
from app import db

load_dotenv() 

app = create_app()

# Asegúrate de que db.create_all() se ejecute dentro del contexto de la aplicación
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv('PORT'))