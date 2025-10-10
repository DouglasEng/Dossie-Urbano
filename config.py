import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    """Configurações da aplicação"""
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'mudar-chave-key-em-producao')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    REQUEST_TIMEOUT = 30
    

    IBGE_API_BASE = os.getenv('IBGE_API_BASE', 'https://servicodados.ibge.gov.br/api/v1')
    NOMINATIM_API_BASE = os.getenv('NOMINATIM_API_BASE', 'https://nominatim.openstreetmap.org')
    OVERPASS_API_BASE = os.getenv('OVERPASS_API_BASE', 'https://overpass-api.de/api/interpreter')


    # config para api openstreetmap
    OSM_USER_AGENT = os.getenv('OSM_USER_AGENT', 'DossieUrbano/1.0 (contato@dossieurbano.com)')
    OSM_REQUEST_DELAY = float(os.getenv('OSM_REQUEST_DELAY', '0.1')) # delay entre requests para respeitar rate limits


    CORS_ORIGINS = ["*"]  