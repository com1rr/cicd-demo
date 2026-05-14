import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    env_name = os.getenv("ENV_NAME", "unknown")
    return f"Hello DevOps from {env_name} environment!"