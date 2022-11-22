from requests import get, post, request
import json
import numpy as np
from FuncoesAuxiliares import *

class GooglePerspectiveApi():
    def chama_api_google_perspective(self, retornoMensagens):
        api_key = 'AIzaSyDPQd2sZX_8qvhon2LJ4SkVlOT5C-GKlHI'
        url = ('https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key=' + api_key)

        array_metricas = []

        for i in range(len(retornoMensagens)):
            frase = retornoMensagens[i][1]

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

                    array_metricas.append(valores_concatenados)

                    #print(json.dumps(response_dict, indent=2))
                except:
                    valores_concatenados =  'Profanidade:' + str(0) + '*' + \
                                            'Toxidade Grave:' + str(0) + '*' + \
                                            'Ataque de Identidade:' + str(0) + '*' + \
                                            'Ameaça:' + str(0) + '*' + \
                                            'Toxidade:' + str(0) + '*' + \
                                            'Insulto:' + str(0) 
                    array_metricas.append(valores_concatenados)
                    pass
            else:
                valores_concatenados = 'Profanidade:' + str(0) + '*' + \
                                        'Toxidade Grave:' + str(0) + '*' + \
                                        'Ataque de Identidade:' + str(0) + '*' + \
                                        'Ameaça:' + str(0) + '*' + \
                                        'Toxidade:' + str(0) + '*' + \
                                        'Insulto:' + str(0) 
                array_metricas.append(valores_concatenados)

        funcoes_auxiliares = FuncoesAuxiliares()
        funcoes_auxiliares.adiciona_nova_coluna('./data/dados_mensagens_aux_polaridade_e_nrc_emotions.csv', './data/dados_metricas.csv', 'GooglePerspectiveMetrics', array_metricas)