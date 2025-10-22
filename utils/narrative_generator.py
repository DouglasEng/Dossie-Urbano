from typing import Dict, List, Any
import random

class NarrativeGenerator:
    """Gerador de narrativas jornalísticas automatizadas"""
    
    def __init__(self):
        self.templates = {
            'seguranca': {
                'alto': [
                    "A região apresenta índices de criminalidade preocupantes, com {crime_type} sendo o principal problema reportado.",
                    "Dados oficiais indicam alta incidência de crimes na área, especialmente {crime_type}, exigindo cautela dos moradores.",
                    "O bairro enfrenta desafios significativos de segurança pública, com registros elevados de {crime_type}."
                ],
                'medio': [
                    "A segurança na região é moderada, com alguns pontos de atenção relacionados a {crime_type}.",
                    "Índices de criminalidade dentro da média municipal, mas com tendência de crescimento em {crime_type}.",
                    "Situação de segurança estável, porém moradores relatam preocupação com {crime_type}."
                ],
                'baixo': [
                    "O bairro apresenta índices de criminalidade abaixo da média municipal, sendo considerado relativamente seguro.",
                    "Região com baixa incidência de crimes, oferecendo maior tranquilidade aos moradores.",
                    "Dados indicam que a área é uma das mais seguras da cidade, com poucos registros de ocorrências."
                ]
            },
            'transporte': {
                'excelente': [
                    "Excelente cobertura de transporte público, com {transport_types} oferecendo conectividade eficiente.",
                    "A região é bem servida por {transport_types}, facilitando o deslocamento para outras áreas da cidade.",
                    "Infraestrutura de transporte de qualidade, com {transport_types} atendendo adequadamente a demanda."
                ],
                'bom': [
                    "Boa disponibilidade de transporte público, principalmente {transport_types}, mas com possíveis melhorias.",
                    "O acesso ao transporte é satisfatório via {transport_types}, embora possa haver superlotação em horários de pico.",
                    "Transporte público funcional através de {transport_types}, atendendo as necessidades básicas de mobilidade."
                ],
                'ruim': [
                    "Limitações significativas no transporte público, com {transport_types} insuficientes para a demanda.",
                    "A região enfrenta desafios de mobilidade, com {transport_types} oferecendo cobertura inadequada.",
                    "Transporte público deficiente, forçando moradores a depender de alternativas como {transport_types}."
                ]
            }
        }
    




    def gerar_narrativa_seguranca(self, security_data: Dict[str, Any]) -> str:
        """Gera narrativa sobre segurança"""
        try:
            taxa_criminalidade = security_data.get('crime_rate', 'desconhecido')
            crime_tipos = security_data.get('main_crime_types', ['crimes diversos'])
            
            if taxa_criminalidade == 'alto':
                template = random.choice(self.templates['seguranca']['alto'])
            elif taxa_criminalidade == 'baixo':
                template = random.choice(self.templates['seguranca']['baixo'])
            else:
                template = random.choice(self.templates['seguranca']['medio'])
            
            main_crime = crime_tipos[0] if crime_tipos else 'crimes diversos'
            
            return template.format(crime_type=main_crime)
            
        except Exception as e:
            return "Dados de segurança não disponíveis para análise detalhada."
        



    
    def gerar_narrativa_transporte(self, transport_data: Dict[str, Any]) -> str:
        """Gera narrativa sobre transporte"""
        try:
            transporte_tipos = transport_data.get('transport_types', [])
            estacoes_contagem = transport_data.get('stations_count', 0)
            
            if estacoes_contagem >= 5:
                level = 'excelente'
            elif estacoes_contagem >= 2:
                level = 'bom'
            else:
                level = 'ruim'
            
            template = random.choice(self.templates['transporte'][level])
            transport_str = ', '.join(transporte_tipos) if transporte_tipos else 'transporte limitado'
            
            return template.format(transport_types=transport_str)
            
        except Exception as e:
            return "Informações de transporte não disponíveis para análise."
    



    def gerar_narrativa_educacao(self, education_data: Dict[str, Any]) -> str:
        """Gera narrativa sobre educação"""
        try:
            escola_contagem = education_data.get('school_count', 0)
            escola_tipos = education_data.get('school_types', [])
            
            if escola_contagem >= 5:
                return f"Região privilegiada em educação, com {escola_contagem} instituições de ensino em um raio de 2km, incluindo {', '.join(escola_tipos)}."
            elif escola_contagem >= 2:
                return f"Boa disponibilidade de escolas, com {escola_contagem} instituições atendendo a região, principalmente {', '.join(escola_tipos)}."
            else:
                return "Limitações na oferta educacional local, com poucas instituições de ensino nas proximidades."
                
        except Exception as e:
            return "Dados educacionais não disponíveis para análise."
        


    
    def gerar_narrativa_saude(self, health_data: Dict[str, Any]) -> str:
        """Gera narrativa sobre saúde"""
        try:
            hospital_contagem = health_data.get('hospital_count', 0)
            farmacia_contagem = health_data.get('pharmacy_count', 0)
            
            if hospital_contagem >= 2 and farmacia_contagem >= 3:
                return f"Excelente infraestrutura de saúde, com {hospital_contagem} hospitais e {farmacia_contagem} farmácias na região."
            elif hospital_contagem >= 1 or farmacia_contagem >= 2:
                return f"Infraestrutura de saúde adequada, com {hospital_contagem} hospital(is) e {farmacia_contagem} farmácia(s) próximas."
            else:
                return "Limitações na infraestrutura de saúde local, com poucos estabelecimentos médicos nas proximidades."
                
        except Exception as e:
            return "Informações de saúde não disponíveis para análise."
        


    
    def gerar_narrativa_comercio(self, commerce_data: Dict[str, Any]) -> str:
        """Gera narrativa sobre comércio"""
        try:
            tipos_comercio = commerce_data.get('commerce_types', [])
            total_estabelicimentos = commerce_data.get('total_establishments', 0)
            
            if total_estabelicimentos >= 10:
                return f"Região comercialmente vibrante, com ampla variedade de estabelecimentos incluindo {', '.join(tipos_comercio)}."
            elif total_estabelicimentos >= 5:
                return f"Boa oferta comercial, com {', '.join(tipos_comercio)} atendendo as necessidades básicas dos moradores."
            else:
                return "Comércio local limitado, com poucos estabelecimentos comerciais nas proximidades."
                
        except Exception as e:
            return "Dados comerciais não disponíveis para análise."
    
    def gerar_narrativa_ambiental(self, environmental_data: Dict[str, Any]) -> str:
        """Gera narrativa sobre meio ambiente"""
        try:
            areas_verdes = environmental_data.get('green_areas', 0)
            qualidade_ar = environmental_data.get('air_quality', 'desconhecida')
            
            if areas_verdes >= 3 and qualidade_ar == 'boa':
                return f"Região com excelente qualidade ambiental, contando com {areas_verdes} áreas verdes e boa qualidade do ar."
            elif areas_verdes >= 1:
                return f"Ambiente moderadamente preservado, com {areas_verdes} área(s) verde(s) e qualidade do ar {qualidade_ar}."
            else:
                return "Limitações ambientais na região, com poucas áreas verdes e qualidade do ar a ser monitorada."
                
        except Exception as e:
            return "Dados ambientais não disponíveis para análise."
        
        
    
    def gerar_analise_final(self, all_data: Dict[str, Any]) -> str:
        """Gera análise final consolidada"""
        try:
            scores = []
            if 'security' in all_data:
                scores.append(all_data['security'].get('safety_score', 5))
            if 'transport' in all_data:
                scores.append(all_data['transport'].get('transport_score', 5))
            if 'environmental' in all_data:
                scores.append(all_data['environmental'].get('environmental_score', 5))
            
            pontuacao_media = sum(scores) / len(scores) if scores else 5
            
            if pontuacao_media >= 7:
                return "Em síntese, a região apresenta condições favoráveis de qualidade de vida, com boa infraestrutura e serviços que atendem adequadamente às necessidades dos moradores."
            elif pontuacao_media >= 5:
                return "A análise revela uma região com qualidade de vida moderada, apresentando alguns pontos positivos mas também desafios que merecem atenção."
            else:
                return "Os dados indicam uma região que enfrenta desafios significativos em termos de qualidade de vida, necessitando de investimentos em infraestrutura e serviços públicos."
                
        except Exception as e:
            return "Análise final não disponível devido à limitação nos dados coletados."