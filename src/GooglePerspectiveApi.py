from threading import Lock
from requests import get, post, request
import json
import numpy as np
from src.FuncoesAuxiliares import *
from concurrent.futures import ThreadPoolExecutor
import time
import collections

#Teste
#from googletrans import Translator  # GoogleTrans para tradução
#import yake  # Para pegar palavras mais utilizadas
#import textstat  # Textstat - pip install textstat - para instalar

class GooglePerspectiveApi():
    def teste(self, frase, indice_frase, dict_metricas, lock):

        while True:
            api_key = 'AIzaSyDPQd2sZX_8qvhon2LJ4SkVlOT5C-GKlHI'
            url = ('https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key=' + api_key)

            #frase = 'APRESENTAÇÃO MEMBROS DA BANCA PITCH Prezadxs; Para conhecimento de vocês, nós conseguimos a colaboração de um "time de peso" para comporem a banca de vocês. São quatro pessoas, sendo duas delas, as professoras Aurora Zen e Luciana Nedel, bastante envolvidas no ecossistema de empreendedorismo dentro de universidades, com experiência nacional e internacional, atuando em atividades de gestão de incubadores, parques tecnológicos, aproximando o universo acadêmico à sociedade e viceversa. Os outros dois membros, Jaime Wagner e Sérgio Finger, são empresários também com um forte envolvimento com empreendedorismo, com experiência na criação de startups e empresas de diferentes de porte. Segue, para conhecimentos de vocês, uma shortbio dos membros da banca (ordem Alfabética): AURORA ZEN, is associate professor in Innovation Management at the Graduate Program of School of Management at the Federal University of Rio Grande do Sul. She has been a Visiting Professor at the Kedge Business School, France, University of Bologna, Italy, Universidad Nacional Del Sur, UNS, Argentina, and Universidad de Antioquia, Medellin, Colombia. She got a PhD. in Business Management at the Federal University of Rio Grande do Sul. Her thesis presented a comparative study between the internationalization strategy of Brazilian and French wineries. She has published many papers and book chapters about international business, strategy, wine industry, innovation, innovation capability, and science parks. Her research interests include international business, strategy, creative economy, wine industry and innovation. JAIME WAGNER, engenheiro eletrônico, mestre em informática e bacharel em filosofia. Fundou as empresas Digitel, Altus, Presenta, Treinar, PowerSelf, WAPT, Vakinha e a WOW Aceleradora. Dirigiu a Plug In Internet e tem longo histórico de atuação em diversas organizações empresariais na promoção do empreendedorismo e do desenvolvimento tecnológico. Blog: http://jaimewagner.com.br/ LUCIANA NEDEL, professora titular no Instituto de Informática da UFRGS desde 2002 e exerce atividades de ensino e pesquisa nas áreas de realidade virtual, visualização interativa e interação humanocomputador. Recebeu o título de doutora em Ciência da Computação pelo Swiss Federal Institute of Tecnology (EPFL) em Lausanne, Suiça, em 1998. Em sua carreira de pesquisadora, tem estado envolvida em projetos com a indústria, bem como em cooperação com várias Universidades no exterior. A mais de 15 anos desenvolve atividades ligadas ao empreendedorismo, sendo que desde junho de 2017 ocupa o cargo de diretora do CEI incubadora (Centro de Empreendimentos em Informática da UFRGS). Na direção do CEI, tem estado envolvida no suporte à geração de startups nas áreas de TI e negócios de impacto, bem como no processo de certificação CERNE. Recentemente, participou do Programa ELI 2019 (Entrepreneurial Leadership & Innovation), no Babson College, em Boston, EUA. SERGIO FINGER, cursou Engenharia da Computação na UFRGS, é Bacharel em Administração pela UFRGS e, atualmente, faz pósgraduação em gestão empresarial pelo Instituto Federal do RS. Foi um dos idealizadores e é cofundador e CEOP da Trashin, startup que realiza gestão de resíduos desde a coleta até a destinação final, utilizando tecnologia para dar escala, segurança e confiabilidade à destinação e valorização de resíduos. Boa apresentação a todos! Erika, Carissimi e Flávio.'
            frase = frase.replace(' ', '') #DESCOMENTAR DPS

            if frase is not np.nan:
                data_dict = {
                'comment': {'text': frase},
                'languages': ['pt'],
                'requestedAttributes': {'TOXICITY': {}, 'IDENTITY_ATTACK': {}, 'PROFANITY': {}, 'SEVERE_TOXICITY': {}, 'THREAT': {}, 'INSULT': {}}
                }

                try:
                    response = post(url=url, data=json.dumps(data_dict))

                    response_dict = json.loads(response.content)

                    valor_profanidade = response_dict['attributeScores']['PROFANITY']['summaryScore']['value']
                    valor_toxicidade_grave = response_dict['attributeScores']['SEVERE_TOXICITY']['summaryScore']['value']
                    valor_ataque_identidade = response_dict['attributeScores']['IDENTITY_ATTACK']['summaryScore']['value']
                    valor_ameaca = response_dict['attributeScores']['THREAT']['summaryScore']['value']
                    valor_toxicidade = response_dict['attributeScores']['TOXICITY']['summaryScore']['value']
                    valor_insulto = response_dict['attributeScores']['INSULT']['summaryScore']['value']

                    valor_media_ameaca_insulto = (valor_ameaca + valor_insulto) / 2
                    valor_media_ataque_identidade_toxicidade = (valor_ataque_identidade + valor_toxicidade) / 2

                    valores_concatenados = 'Profanidade:' + str(valor_profanidade) + '*' + \
                                        'Toxicidade Grave:' + str(valor_toxicidade_grave) + '*' + \
                                        'Ataque de Identidade:' + str(valor_ataque_identidade) + '*' + \
                                        'Ameaça:' + str(valor_ameaca) + '*' + \
                                        'Toxicidade:' + str(valor_toxicidade) + '*' + \
                                        'Insulto:' + str(valor_insulto)  + '*' + \
                                        'Media_A_I:' + str(valor_media_ameaca_insulto) + '*' + \
                                        'Media_A_T:' + str(valor_media_ataque_identidade_toxicidade)
                    
                    #return valores_concatenados
                    lock.acquire()
                    dict_metricas[indice_frase] = valores_concatenados
                    self.contador_global += 1
                    self.funcoes_auxiliares.barra_progresso(self.contador_global, self.tamanho_mensanges, 'Agregando')
                    lock.release()
                    
                    break
                    
                    
                except:
                    time.sleep(1)
                    continue
            else:
                valores_concatenados = 'Profanidade:' + str(0) + '*' + \
                                        'toxicidade Grave:' + str(0) + '*' + \
                                        'Ataque de Identidade:' + str(0) + '*' + \
                                        'Ameaça:' + str(0) + '*' + \
                                        'toxicidade:' + str(0) + '*' + \
                                        'Insulto:' + str(0) + '*' + \
                                        'Media_A_I:' + str(0) + '*' + \
                                        'Media_A_T:' + str(0)
                #return valores_concatenados
                lock.acquire()
                dict_metricas[indice_frase] = valores_concatenados
                self.contador_global += 1
                self.funcoes_auxiliares.barra_progresso(self.contador_global, self.tamanho_mensanges, 'Agregando')
                lock.release()
                
                break
                
    def chama_api_google_perspective(self, retornoMensagens):
        dict_metricas = {}
        self.funcoes_auxiliares = FuncoesAuxiliares()
        self.contador_global = 0

        pool = ThreadPoolExecutor()
        lock = Lock()

        self.tamanho_mensanges = len(retornoMensagens)

        for i in range(len(retornoMensagens)):#
            frase = retornoMensagens[i][1].replace('\\', '\\\\')
            
            pool.submit(self.teste, frase, i+1, dict_metricas, lock) #Primeiro parametro é a função e os outros são os parametros pra função

            
        pool.shutdown(wait=True)
        print()

        dict_emocoes_nrc_ordenado = collections.OrderedDict(sorted(dict_metricas.items()))
        self.funcoes_auxiliares.adiciona_nova_coluna_dict('./data/dados_mensagens_aux_polaridade_e_nrc_emotions.csv', './data/dados_metricas.csv', 'GooglePerspectiveMetrics', dict_emocoes_nrc_ordenado)