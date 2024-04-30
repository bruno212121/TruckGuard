from flask_restful import Resource
from flask import request, jsonify
from .. import db
from ..models import MaintenanceModel
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

class Maintenance(Resource):

    @jwt_required
    def get(self, id):
        maintenance = db.session.query(MaintenanceModel).get_or_404(id)
        return maintenance.to_json()

    #realizar decorador para owner y driver
    def put(self, id):
        pass

    #realizar decorador para owner y driver
    def patch(self, id):
         pass

    #realizar decorador para owner y driver
    def post(self):
        pass