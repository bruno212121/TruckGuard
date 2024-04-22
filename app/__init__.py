import os 
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from dotenv import load_dotenv 


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    lload_dotenv()


    if not os.path.exists(os.getenv('DATABASE_PATH') + os.getenv('DATABASE_NAME')): # Check if the database exists
        os.mknod(os.getenv('DATABASE_PATH') + os.getenv('DATABASE_NAME')) 
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable the modification tracker

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.getenv('DATABASE_PATH') + os.getenv('DATABASE_NAME') 
    db.init_app(app)


 