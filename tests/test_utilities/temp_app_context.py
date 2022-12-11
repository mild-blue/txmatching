from flask import Flask

def create_temp_app_context():
    app = Flask(__name__)
    app.config['SERVER_NAME'] = 'test'
    app.config['POSTGRES_USER'] = 'str'
    app.config['POSTGRES_PASSWORD'] = 'str'
    app.config['POSTGRES_DB'] = 'str'
    app.config['POSTGRES_URL'] = 'str'
    app.config['JWT_SECRET'] = 'str'
    app.config['JWT_EXPIRATION_DAYS'] = 10
    app.config['ENVIRONMENT'] = 'PRODUCTION'
    app.config['HLA_PARSING'] = 'STRICT'
    app.config['COLOUR_SCHEME'] = 'IKEM'
    app.config['USE_2FA'] = 'FALSE'
    app.config['AUTHENTIC_CLIENT_ID'] = 'f5c6b6a72ff4f7bbdde383a26bdac192b2200707'
    app.config['AUTHENTIC_CLIENT_SECRET'] = '37e841e70b842a0d1237b3f7753b5d7461307562568b5add7edcfa66' \
                                                    '30d578fdffb7ff4d5c0f845d10f8f82bc1d80cec62cb397fd48795a5b1b' \
                                                    'ee6090e0fa409'
    app.config['AUTHENTIC_REDIRECT_URI'] = 'http://localhost:8080/v1/user/authentik-login'

    return app
