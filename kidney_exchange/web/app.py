import logging

from kidney_exchange.web import create_app

app = create_app()
logger = logging.getLogger(__name__)

# For flask.flash (gives feedback when uploading files)
app.secret_key = "secret key"
# Add config
app.config["CSV_UPLOADS"] = "kidney_exchange/web/csv_uploads"
app.config["ALLOWED_CSV_EXTENSIONS"] = ["CSV", "XLSX"]


# register blueprints
app.register_blueprint(service_api)
app.register_blueprint(functional_api)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
