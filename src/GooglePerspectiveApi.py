from src.FuncoesAuxiliares import *

from threading import Lock
from requests import post
from json import loads, dumps
from unidecode import unidecode
from numpy import nan
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from collections import OrderedDict
from googletrans import Translator  # GoogleTrans para tradução
import textstat  # Textstat - pip install textstat - para instalar

class GooglePerspectiveApi():
    def tratamento_thread(self, frase, indice_frase, dict_metricas, lock):
        while True:
            api_key = ''
            url = ('https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key=' + api_key)

            if frase is not nan:
                textstat.set_lang('en')
                translator = Translator()

                frase = unidecode(frase)
                frase_traduzida = translator.translate(frase, src='pt', dest='en')
                frase_traduzida.text = frase_traduzida.text.replace('\u200b', '')

                data_dict = {
                'comment': {'text': frase_traduzida.text},
                'languages': ['en'],
                'requestedAttributes': {'TOXICITY': {}, 'IDENTITY_ATTACK': {}, 'PROFANITY': {}, 'SEVERE_TOXICITY': {}, 'THREAT': {}, 'INSULT': {}}
                }

                try:
                    response = post(url=url, data=dumps(data_dict))
                    response_dict = loads(response.content)

                    valor_profanidade = response_dict['attributeScores']['PROFANITY']['summaryScore']['value']
                    valor_toxicidade_severa = response_dict['attributeScores']['SEVERE_TOXICITY']['summaryScore']['value']
                    valor_ataque_identidade = response_dict['attributeScores']['IDENTITY_ATTACK']['summaryScore']['value']
                    valor_ameaca = response_dict['attributeScores']['THREAT']['summaryScore']['value']
                    valor_toxicidade = response_dict['attributeScores']['TOXICITY']['summaryScore']['value']
                    valor_insulto = response_dict['attributeScores']['INSULT']['summaryScore']['value']

                    valores_concatenados = 'Profanidade:' + str(valor_profanidade) + '*' + \
                                        'Toxicidade Severa:' + str(valor_toxicidade_severa) + '*' + \
                                        'Ataque de Identidade:' + str(valor_ataque_identidade) + '*' + \
                                        'Ameaça:' + str(valor_ameaca) + '*' + \
                                        'Toxicidade:' + str(valor_toxicidade) + '*' + \
                                        'Insulto:' + str(valor_insulto)
                    
                    #return valores_concatenados
                    lock.acquire()
                    dict_metricas[indice_frase] = valores_concatenados
                    self.contador_global += 1
                    self.funcoes_auxiliares.barra_progresso(self.contador_global, self.tamanho_mensanges, 'Agrupando')
                    lock.release()
                    
                    break 
                except:
                    sleep(1)
                    continue
            else:
                valores_concatenados = 'Profanidade:' + str(0) + '*' + \
                                        'Toxicidade Severa:' + str(0) + '*' + \
                                        'Ataque de Identidade:' + str(0) + '*' + \
                                        'Ameaça:' + str(0) + '*' + \
                                        'Toxicidade:' + str(0) + '*' + \
                                        'Insulto:' + str(0)
                lock.acquire()
                dict_metricas[indice_frase] = valores_concatenados
                self.contador_global += 1
                self.funcoes_auxiliares.barra_progresso(self.contador_global, self.tamanho_mensanges, 'Agrupando')
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
            pool.submit(self.tratamento_thread, frase, i+1, dict_metricas, lock) #Primeiro parametro é a função e os outros são os parametros pra função

        pool.shutdown(wait=True)
        print()

        dict_emocoes_nrc_ordenado = OrderedDict(sorted(dict_metricas.items()))
        self.funcoes_auxiliares.adiciona_nova_coluna_dict('./data/dados_mensagens_aux_polaridade_e_emo_roberta_emocoes.csv', './data/dados_metricas.csv', 'GooglePerspectiveMetrics', dict_emocoes_nrc_ordenado)