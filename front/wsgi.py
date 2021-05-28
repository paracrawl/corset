# Used by gunicorn to run the app
from front.app import app

if __name__ == "__main__":
    app.run()
