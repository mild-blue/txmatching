import logging

from kidney_exchange.web import create_app

app = create_app()
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
