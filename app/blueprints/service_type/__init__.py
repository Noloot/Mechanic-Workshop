from flask import Blueprint

serviceType_bp = Blueprint("serviceType_bp", __name__)

from . import routes