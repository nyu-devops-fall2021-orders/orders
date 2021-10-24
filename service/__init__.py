import sys
from flask import Flask

app = Flask(__name__)

from service import routes
app.config.from_object("config")

try:
    routes.init_db()  # make our sqlalchemy tables
except Exception as error:
    # gunicorn requires exit code 4 to stop spawning workers when they die
    sys.exit(4)
