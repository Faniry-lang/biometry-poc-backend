from datetime import datetime
from flask import Flask, jsonify, request, abort
from database import db
from models import Client
import os

app = Flask(__name__)

USERNAME = 'root'
PASSWORD = 'root'
HOST = 'localhost'
PORT = '3306'
DB_NAME = 'agdbk_biometry_poc'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

FINGERPRINT_KEY = 'VC6v8iWsGP3hsPGT5gTPYAQTiMSdWIPNkTB9jhEwtWE='         # base64-encoded 32-byte AES key
KEY_ENDPOINT_SECRET = 'PyXeIdCuVs0gf5m4P6lLHPUqxOBwYCAC5e0hTuuo7qE='  # shared secret gating this endpoint

db.init_app(app)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

@app.route('/')
def hello_world():
    return 'Hello world'

@app.route('/clients', methods=['POST', 'OPTIONS'])
def create_client():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json(silent=True) or {}
    try:
        client = Client(
            Firstnames=data.get('Firstnames'),
            Lastname=data.get('Lastname'),
            Telephone=data.get('Telephone') or None,
            Email=data.get('Email') or None,
            IdentityNumber=data.get('IdentityNumber') or None,
            IsEnabled=data.get('IsEnabled', '1'),
            Comments=data.get('Comments'),
            BankIdClient=data.get('BankIdClient'),
            DateTimeCreated=datetime.utcnow()
        )
        db.session.add(client)
        db.session.commit()
        return jsonify({'message': 'Client created', 'id': client.IdClient}), 201
    except Exception as err:
        db.session.rollback()
        return jsonify({'error': str(err)}), 400

@app.route('/clients/<int:client_id>/fingerprint', methods=['PUT', 'OPTIONS'])
def add_fingerprint(client_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json(silent=True) or {}
    client = db.session.get(Client, client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404

    fp = data.get('fingerprint')
    if fp is not None:
        if isinstance(fp, str):
            client.Fingerprint = fp.encode('utf-8')
        elif isinstance(fp, bytes):
            client.Fingerprint = fp

    client.DateTimeModified = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Fingerprint updated'}), 200

@app.route('/get-client-by-id', methods=['GET', 'OPTIONS'])
def get_client_by_id():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    client_id = request.args.get('id', type=int)
    if not client_id:
        return jsonify({'error': 'Client ID required'}), 400

    client = db.session.get(Client, client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404

    return jsonify({
        'id': client.IdClient,
        'firstnames': client.Firstnames,
        'lastname': client.Lastname,
        'telephone': client.Telephone,
        'email': client.Email,
        'identityNumber': client.IdentityNumber,
        'isEnabled': client.IsEnabled,
        'comments': client.Comments,
        'dateTimeCreated': client.DateTimeCreated.isoformat() if client.DateTimeCreated else None,
        'dateTimeModified': client.DateTimeModified.isoformat() if client.DateTimeModified else None,
        'bankIdClient': client.BankIdClient,
        'dateTimeActivationToggle': client.DateTimeActivationToggle.isoformat() if client.DateTimeActivationToggle else None
    }), 200

@app.route('/get-finger-print-by-clientid', methods=['GET', 'OPTIONS'])
def get_fingerprint_by_client_id():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    client_id = request.args.get('id', type=int)
    if not client_id:
        return jsonify({'error': 'Client ID required'}), 400

    client = db.session.get(Client, client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404

    fingerprint = None
    if client.Fingerprint is not None:
        if isinstance(client.Fingerprint, bytes):
            try:
                fingerprint = client.Fingerprint.decode('utf-8')
            except UnicodeDecodeError:
                import base64
                fingerprint = base64.b64encode(client.Fingerprint).decode('utf-8')
        else:
            fingerprint = str(client.Fingerprint)

    return jsonify({'fingerprint': fingerprint}), 200

@app.route('/get-key', methods=['GET', 'OPTIONS'])
def get_key():
    if request.method == 'OPTIONS':
        return app.make_default_options_response()

    provided_secret = request.headers.get('X-Api-Key')
    if not provided_secret or provided_secret != KEY_ENDPOINT_SECRET:
        abort(401, description="Missing or invalid API key")

    if not FINGERPRINT_KEY:
        abort(500, description="Encryption key not configured")

    return jsonify({"key": FINGERPRINT_KEY})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)