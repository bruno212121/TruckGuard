from app import create_app
import os 
from dotenv import load_dotenv
from app import db

load_dotenv() 
app = create_app()
app.app_context().push()

from app import db

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port= os.getenv('PORT'))