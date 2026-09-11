from datetime import datetime
from operator import and_
from flask import Flask, jsonify, request, abort
from database import db
from models import Client, Fingerprint
from config import DB_URI, FINGERPRINT_KEY, KEY_ENDPOINT_SECRET
from flask_migrate import Migrate
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

FINGER_LABELS = [
    'left_thumb', 
    'left_index', 
    'left_middle', 
    'left_ring', 
    'left_little',
    'right_thumb', 
    'right_index', 
    'right_middle', 
    'right_ring', 
    'right_little'
]

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

@app.route('/')
def hello_world():
    return 'Hello world'

@app.route('/get-finger-labels', methods=['GET', 'OPTIONS'])
def get_finger_labels():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    return jsonify({'fingerlabels': FINGER_LABELS}), 200

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

    # Get fingerprint label
    fingerprint_label = request.args.get('label')

    if not fingerprint_label:
        return jsonify({
            'error': 'Fingerprint label is required'
        }), 400

    # Get client
    client = db.session.get(Client, client_id)

    if not client:
        return jsonify({
            'error': 'Client not found'
        }), 404

    # Get request data
    data = request.get_json(silent=True) or {}

    fingerprint_data = data.get('fingerprint')
    iv = data.get('iv')
    tag = data.get('tag')

    if fingerprint_data is None:
        return jsonify({
            'error': 'Fingerprint data is required'
        }), 400

    if iv is None:
        return jsonify({
            'error': 'IV is required'
        }), 400

    if tag is None:
        return jsonify({
            'error': 'Tag is required'
        }), 400

    # Convert fingerprint data to bytes
    if isinstance(fingerprint_data, str):
        fingerprint_data = fingerprint_data.encode('utf-8')
    elif not isinstance(fingerprint_data, bytes):
        return jsonify({
            'error': 'Invalid fingerprint data'
        }), 400

    try:
        now = datetime.utcnow()

        # Find existing fingerprint for this client and label
        existing_fingerprint = Fingerprint.query.filter(
            and_(
                Fingerprint.IdClient == client_id,
                Fingerprint.FingerprintLabel == fingerprint_label,
                Fingerprint.RevokedAt.is_(None)
            )
        ).first()

        # Revoke existing fingerprint
        if existing_fingerprint:
            existing_fingerprint.RevokedAt = now

        # Create new fingerprint
        new_fingerprint = Fingerprint(
            IdClient=client_id,
            FingerprintLabel=fingerprint_label,
            CipherText=fingerprint_data,
            IV=iv,
            Tag=tag,
            CreatedAt=now,
            RevokedAt=None
        )

        db.session.add(new_fingerprint)

        # Update client modification date
        client.DateTimeModified = now

        db.session.commit()

        return jsonify({
            'message': 'Fingerprint added successfully',
            'IdFingerprint': new_fingerprint.IdFingerprint,
            'FingerprintLabel': new_fingerprint.FingerprintLabel
        }), 200

    except Exception as e:
        db.session.rollback()

        return jsonify({
            'error': 'Failed to add fingerprint',
            'details': str(e)
        }), 500

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

@app.route('/get-fingerprints-by-clientid', methods=['GET', 'OPTIONS'])
def get_fingerprints_by_clientid():

    if request.method == 'OPTIONS':
        return jsonify({}), 200

    client_id = request.args.get('id', type=int)

    if not client_id:
        return jsonify({
            'error': 'Client ID required'
        }), 400

    client = db.session.get(Client, client_id)

    if not client:
        return jsonify({
            'error': 'Client not found'
        }), 404

    fingerprints = []

    for fingerprint in client.Fingerprints:
        fingerprints.append({
            'IdFingerprint': fingerprint.IdFingerprint,
            'IdClient': fingerprint.IdClient,
            'FingerprintLabel': fingerprint.FingerprintLabel,
            'CipherText': fingerprint.CipherText.hex(),
            'IV': fingerprint.IV,
            'Tag': fingerprint.Tag,
            'CreatedAt': fingerprint.CreatedAt.isoformat()
                if fingerprint.CreatedAt else None,
            'RevokedAt': fingerprint.RevokedAt.isoformat()
                if fingerprint.RevokedAt else None
        })

    return jsonify({
        'fingerprints': fingerprints
    }), 200

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

@app.route('/search-clients', methods=['GET', 'OPTIONS'])
def search_clients():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    query = request.args.get('query', '')
    if not query:
        return jsonify({'clients': []}), 200

    clients = Client.query.filter(
        (Client.Firstnames.ilike(f'%{query}%')) | (Client.Lastname.ilike(f'%{query}%'))
    ).all()

    return jsonify({
        'clients': [
            {
                'id': c.IdClient,
                'firstnames': c.Firstnames,
                'lastname': c.Lastname,
                'telephone': c.Telephone,
                'email': c.Email,
                'identityNumber': c.IdentityNumber,
            }
            for c in clients
        ]
    }), 200

@app.route('/clients/<int:client_id>/fingerprints/status', methods=['GET', 'OPTIONS'])
def get_fingerprint_status(client_id):

    if request.method == 'OPTIONS':
        return jsonify({}), 200

    # Check that the client exists
    client = db.session.get(Client, client_id)

    if not client:
        return jsonify({
            'error': 'Client not found'
        }), 404

    # Get active fingerprints for this client
    registered_labels = {
        fingerprint.FingerprintLabel
        for fingerprint in client.Fingerprints
        if fingerprint.RevokedAt is None
    }

    # Build status for every possible finger
    fingerprint_status = {
        label: label in registered_labels
        for label in FINGER_LABELS
    }

    return jsonify(fingerprint_status), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)