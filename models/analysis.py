from typing import Dict, Any, Optional
from services.ibge_service import IBGEService
from services.maps_service import MapsService
from services.security_service import SecurityService
from utils.narrative_generator import NarrativeGenerator

class UrbanAnalysis:
    """Modelo principal para análise urbana completa"""
    
    def __init__(self):
        self.ibge_service = IBGEService()
        self.maps_service = MapsService()
        self.security_service = SecurityService()
        self.narrative_generator = NarrativeGenerator()
    
    def analyze_neighborhood(self, endereco: str) -> Dict[str, Any]:
        """Realiza análise completa de um bairro/endereço"""
        try:
            location_data = self.maps_service.geocode_address(endereco)
            if not location_data:
                return {
                    'error': 'Endereço não encontrado',
                    'message': 'Não foi possível localizar o endereço informado. Verifique se está correto e tente novamente.'
                }
            
            latitude = location_data['latitude']
            longitude = location_data['longitude']
            componentes = location_data['componentes']
            
            bairro = componentes.get('bairro', 'Não identificado')
            cidade = componentes.get('cidade', 'Não identificada')
            estado = componentes.get('estado', 'Não identificado')
            
            demographic_data = {}
            if cidade != 'Não identificada' and estado != 'Não identificado':
                demographic_data = self.ibge_service.get_municipio_info(cidade, estado) or {}
            
            security_data = self.security_service.analyze_security(cidade, estado, bairro)
            
            transport_data = self.maps_service.analyze_transport(latitude, longitude)
            
            infrastructure_data = self.maps_service.analyze_infrastructure(latitude, longitude)
            
            education_data = self._process_education_data(infrastructure_data)
            health_data = self._process_health_data(infrastructure_data)
            commerce_data = self._process_commerce_data(infrastructure_data)
            environmental_data = self._process_environmental_data(latitude, longitude)
            
            narratives = self._generate_narratives({
                'security': security_data,
                'transport': transport_data,
                'education': education_data,
                'health': health_data,
                'commerce': commerce_data,
                'environmental': environmental_data
            })
            
            final_analysis = self.narrative_generator.generate_final_analysis({
                'security': security_data,
                'transport': transport_data,
                'education': education_data,
                'health': health_data,
                'commerce': commerce_data,
                'environmental': environmental_data
            })
            
            result = {
                'bairro': bairro,
                'cidade': cidade,
                'estado': estado,
                'coordenadas': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'endereco_formatado': location_data['endereco_formatado'],
                
                #narrativas por categoria
                'seguranca': narratives['security'],
                'transporte': narratives['transport'],
                'educacao': narratives['education'],
                'saude': narratives['health'],
                'comercio': narratives['commerce'],
                'ambiental': narratives['environmental'],
                
                'analise_final': final_analysis,
                
                'dados_brutos': {
                    'demografia': demographic_data,
                    'seguranca': security_data,
                    'transporte': transport_data,
                    'infraestrutura': infrastructure_data
                },
                
                # Metadados
                'timestamp': self._get_timestamp(),
                'fonte_dados': 'Múltiplas fontes públicas e APIs abertas'
            }
            
            return result
            
        except Exception as e:
            return {
                'error': 'Erro na análise',
                'message': f'Ocorreu um erro durante a análise: {str(e)}',
                'details': 'Tente novamente ou verifique se o endereço está correto.'
            }
    
    def _process_education_data(self, infrastructure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa dados educacionais da infraestrutura"""
        escolas_data = infrastructure_data.get('escolas', {})
        
        school_count = escolas_data.get('count', 0)
        schools = escolas_data.get('places', [])
        
        school_types = []
        for school in schools:
            name = school.get('nome', '').lower()
            if 'municipal' in name or 'emef' in name:
                school_types.append('escola municipal')
            elif 'estadual' in name or 'eef' in name:
                school_types.append('escola estadual')
            elif 'particular' in name or 'colégio' in name:
                school_types.append('escola particular')
            else:
                school_types.append('escola pública')
        
        return {
            'school_count': school_count,
            'school_types': list(set(school_types)) or ['escolas públicas'],
            'schools_nearby': schools[:3],  # top 3 mais proximas
            'score': escolas_data.get('score', 0)
        }
    
    def _process_health_data(self, infrastructure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa dados de saúde da infraestrutura"""
        hospitais = infrastructure_data.get('hospitais', {}).get('places', [])
        farmacias = infrastructure_data.get('farmacias', {}).get('places', [])
        
        health_facilities = []
        
        for hospital in hospitais:
            health_facilities.append({
                'name': hospital.get('nome'),
                'type': 'hospital',
                'distance': None  
            })
        
        for farmacia in farmacias:
            health_facilities.append({
                'name': farmacia.get('nome'),
                'type': 'farmácia',
                'distance': None
            })
        
        return {
            'health_facilities': health_facilities,
            'hospital_count': len(hospitais),
            'pharmacy_count': len(farmacias),
            'total_facilities': len(health_facilities)
        }
    
    def _process_commerce_data(self, infrastructure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa dados comerciais da infraestrutura"""
        commerce_types = []
        
        #mapeia categorias de infraestrutura para tipos comerciais
        category_mapping = {
            'supermercados': 'supermercados',
            'restaurantes': 'restaurantes',
            'bancos': 'bancos',
            'farmacias': 'farmácias'
        }
        
        for category, commerce_type in category_mapping.items():
            if infrastructure_data.get(category, {}).get('count', 0) > 0:
                commerce_types.append(commerce_type)
        
        return {
            'commerce_types': commerce_types,
            'total_establishments': sum(
                infrastructure_data.get(cat, {}).get('count', 0) 
                for cat in category_mapping.keys()
            )
        }
    
    def _process_environmental_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Processa dados ambientais (simulado - em produção integraria com APIs específicas)"""

        import random
        
        green_areas = random.randint(0, 5)
        
        air_quality_options = ['boa', 'moderada', 'ruim', 'desconhecida']
        air_quality = random.choice(air_quality_options)
        
        return {
            'green_areas': green_areas,
            'air_quality': air_quality,
            'environmental_score': random.randint(3, 8)
        }
    
    def _generate_narratives(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Gera narrativas para cada categoria"""
        return {
            'security': self.narrative_generator.generate_security_narrative(data['security']),
            'transport': self.narrative_generator.generate_transport_narrative(data['transport']),
            'education': self.narrative_generator.generate_education_narrative(data['education']),
            'health': self.narrative_generator.generate_health_narrative(data['health']),
            'commerce': self.narrative_generator.generate_commerce_narrative(data['commerce']),
            'environmental': self.narrative_generator.generate_environmental_narrative(data['environmental'])
        }
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_analysis_summary(self, endereco: str) -> Dict[str, Any]:
        """Retorna resumo rápido da análise (versão simplificada)"""
        try:
            full_analysis = self.analyze_neighborhood(endereco)
            
            if 'error' in full_analysis:
                return full_analysis
            
            return {
                'bairro': full_analysis['bairro'],
                'cidade': full_analysis['cidade'],
                'resumo': {
                    'seguranca': full_analysis['seguranca'][:100] + '...',
                    'transporte': full_analysis['transporte'][:100] + '...',
                    'infraestrutura': f"Região com {full_analysis['dados_brutos']['infraestrutura'].get('escolas', {}).get('count', 0)} escolas próximas"
                },
                'coordenadas': full_analysis['coordenadas']
            }
            
        except Exception as e:
            return {
                'error': 'Erro no resumo',
                'message': str(e)
            }