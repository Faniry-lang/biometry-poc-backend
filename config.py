import os
from dotenv import load_dotenv

load_dotenv()

FINGERPRINT_KEY = os.environ.get('FINGERPRINT_KEY', 'VC6v8iWsGP3hsPGT5gTPYAQTiMSdWIPNkTB9jhEwtWE=')
KEY_ENDPOINT_SECRET = os.environ.get('KEY_ENDPOINT_SECRET', 'PyXeIdCuVs0gf5m4P6lLHPUqxOBwYCAC5e0hTuuo7qE=')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'agdbk_biometry_poc')

DB_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
