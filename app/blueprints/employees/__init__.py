from flask import Blueprint

employee_bp = Blueprint('employee_bp', __name__)

from . import routes

