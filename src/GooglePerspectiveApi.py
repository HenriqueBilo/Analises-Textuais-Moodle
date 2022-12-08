from threading import Lock
from requests import get, post, request
import json
import numpy as np
from src.FuncoesAuxiliares import *
from concurrent.futures import ThreadPoolExecutor
import time
import collections

class GooglePerspectiveApi():

    def teste(self, frase, indice_frase, dict_metricas, lock):

        while True:
            api_key = ''
            url = ('https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key=' + api_key)

            if frase is not np.nan:
                data_dict = {
                'comment': {'text': frase},
                'languages': ['pt'],
                'requestedAttributes': {'TOXICITY': {}, 'IDENTITY_ATTACK': {}, 'PROFANITY': {}, 'SEVERE_TOXICITY': {}, 'THREAT': {}, 'INSULT': {}}
                }

                try:
                    response = post(url=url, data=json.dumps(data_dict))
                    #contador = 1
                    '''while response.status_code != 200:
                        time.sleep(1)
                        response = post(url=url, data=json.dumps(data_dict))
                        contador += 1
                        #print('Entrou no retry')'''

                    response_dict = json.loads(response.content)

                    valor_profanidade = response_dict['attributeScores']['PROFANITY']['summaryScore']['value']
                    valor_toxidade_grave = response_dict['attributeScores']['SEVERE_TOXICITY']['summaryScore']['value']
                    valor_ataque_identidade = response_dict['attributeScores']['IDENTITY_ATTACK']['summaryScore']['value']
                    valor_ameaca = response_dict['attributeScores']['THREAT']['summaryScore']['value']
                    valor_toxidade = response_dict['attributeScores']['TOXICITY']['summaryScore']['value']
                    valor_insulto = response_dict['attributeScores']['INSULT']['summaryScore']['value']

                    valores_concatenados = 'Profanidade:' + str(valor_profanidade) + '*' + \
                                        'Toxidade Grave:' + str(valor_toxidade_grave) + '*' + \
                                        'Ataque de Identidade:' + str(valor_ataque_identidade) + '*' + \
                                        'Ameaça:' + str(valor_ameaca) + '*' + \
                                        'Toxidade:' + str(valor_toxidade) + '*' + \
                                        'Insulto:' + str(valor_insulto) 
                    
                    #return valores_concatenados
                    #with lock:
                    dict_metricas[indice_frase] = valores_concatenados
                    break
                    #lock.release()
                    
                except:
                    time.sleep(1)
                    '''valores_concatenados =  'Profanidade:' + str(0) + '*' + \
                                            'Toxidade Grave:' + str(0) + '*' + \
                                            'Ataque de Identidade:' + str(0) + '*' + \
                                            'Ameaça:' + str(0) + '*' + \
                                            'Toxidade:' + str(0) + '*' + \
                                            'Insulto:' + str(0) 
                    with lock:
                        array_metricas.append(valores_concatenados)'''
                    #print('Caiu na excecao mesmo assim')
                    #pass
                    continue
            else:
                valores_concatenados = 'Profanidade:' + str(0) + '*' + \
                                        'Toxidade Grave:' + str(0) + '*' + \
                                        'Ataque de Identidade:' + str(0) + '*' + \
                                        'Ameaça:' + str(0) + '*' + \
                                        'Toxidade:' + str(0) + '*' + \
                                        'Insulto:' + str(0) 
                #return valores_concatenados
                #with lock:
                dict_metricas[indice_frase] = valores_concatenados
                break
                #lock.release()
                

    def chama_api_google_perspective(self, retornoMensagens):
        array_metricas = []
        dict_metricas = {}

        pool = ThreadPoolExecutor()

        lock = Lock()

        #with ThreadPoolExecutor() as executor:
        for i in range(len(retornoMensagens)):#
            frase = retornoMensagens[i][1].replace('\\', '\\\\')
            #r'Prezados alunos,  Espero que estejam todos bem. Gostaríamos de avisar que estão disponíveis no Moodle da disciplina as notas e conceitos de  Cálculo Lambda e Teoria dos Tipos (Graduação)  Foundations for Rigorous Software Development (Pósgraduação)  Gostaríamos de pedir desculpas pela grande demora na correção da Lista 4 e entrega dos conceitos finais da disciplina. O reinício das atividades no formato ERE, em particular a gravação de videoaulas para demais disciplinas acabou contribuindo para esse atraso.  Sobre a recuperação de conceito: vamos solicitar que quem queira incrementar a sua nota/conceito, que nos envie até o final do semestre versões revisadas das listas enviadas previamente, contendo correções, até o último encontro da disciplina (na próxima semana).  Sobre a finalização das atividades, e correção das listas: gostaríamos de marcar um último encontro de despedida da disciplina:  ENCONTRO SÍNCRONO FINAL Data: próxima quintafeira, 26/Novembro Horário: 13:3015:30 Local: Mconf, link disponível no Moodle  A ideia é revisar as Listas de Exercícios, discutir o conteúdo do semestre como um todo e receber feedback de vocês sobre as melhorias que a disciplina pode ter para os próximos semestres.  Bom final de semestre a todos! Rodrigo e Alvaro' 
            #
            pool.submit(self.teste, frase, i+1, dict_metricas, lock) #Primeiro parametro é a função e os outros são os parametros pra função
            #time.sleep(2)
            #array_metricas.append(retorno.result())

        pool.shutdown(wait=True)

        dict_emocoes_nrc_ordenado = collections.OrderedDict(sorted(dict_metricas.items()))

        funcoes_auxiliares = FuncoesAuxiliares()
        funcoes_auxiliares.adiciona_nova_coluna_dict('./data/dados_mensagens_aux_polaridade_e_nrc_emotions.csv', './data/dados_metricas.csv', 'GooglePerspectiveMetrics', dict_emocoes_nrc_ordenado)