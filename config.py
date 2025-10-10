import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    """Configurações da aplicação"""
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'mudar-chave-key-em-producao')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    REQUEST_TIMEOUT = 30
    
    IBGE_API_BASE = os.getenv('IBGE_API_BASE', 'https://servicodados.ibge.gov.br/api/v1')


    CORS_ORIGINS = ["*"]  