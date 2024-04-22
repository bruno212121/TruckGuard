from app import create_app
import os 

app = create_app()


from app import db

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port= os.getenv('PORT'))