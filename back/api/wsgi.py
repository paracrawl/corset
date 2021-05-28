# Used by gunicorn to run the app
from back.api.app import app

if __name__ == "__main__":
    app.run()
