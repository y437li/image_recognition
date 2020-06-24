from flask import Flask
from flask_material import Material

app = Flask(__name__)
Material(app)
app.config.from_object('setting')

from image_rec import views
