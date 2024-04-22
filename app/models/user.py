from .. import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))


    owner = db.relationship('Owner', back_populates='user')
    driver = db.relationship('Driver', back_populates='user')
