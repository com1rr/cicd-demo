import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    env_name = os.getenv("ENV_NAME", "unknown")
    demo_secret = os.getenv("DEMO_SECRET", "")

    secret_loaded = "yes" if demo_secret else "no"

    return f"Hello DevOps from {env_name} environment! Secret loaded: {secret_loaded}"