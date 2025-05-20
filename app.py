from app import create_app
from app.models import db


app = create_app('DevelopmentConfig')

@app.route('/')
def home():
    return "Home"

with app.app_context():
    # db.drop_all()
    db.create_all()
    

app.run()