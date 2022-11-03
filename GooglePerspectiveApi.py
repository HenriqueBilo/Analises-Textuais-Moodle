from requests import get, post, request
import json
from FuncoesAuxiliares import *

class GooglePerspectiveApi():
    def chama_api_google_perspective(self, retornoMensagens):
        api_key = ''
        url = ('https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key=' + api_key)

        array_metricas = []

        for i in range(len(retornoMensagens)):
            frase = retornoMensagens[i][1]

            data_dict = {
            'comment': {'text': frase},
            'languages': ['pt'],
            'requestedAttributes': {'TOXICITY': {}, 'IDENTITY_ATTACK': {}, 'PROFANITY': {}, 'SEVERE_TOXICITY': {}, 'THREAT': {}}
            }

            try:
                response = post(url=url, data=json.dumps(data_dict))
                response_dict = json.loads(response.content)

                valor_profanidade = response_dict['attributeScores']['PROFANITY']['summaryScore']['value']
                valor_toxidade_grave = response_dict['attributeScores']['SEVERE_TOXICITY']['summaryScore']['value']
                valor_ataque_identidade = response_dict['attributeScores']['IDENTITY_ATTACK']['summaryScore']['value']
                valor_ameaca = response_dict['attributeScores']['THREAT']['summaryScore']['value']
                valor_toxidade = response_dict['attributeScores']['TOXICITY']['summaryScore']['value']

                valores_concatenados = 'Profanidade:' + str(valor_profanidade) + '*' + \
                                    'Toxidade Grave:' + str(valor_toxidade_grave) + '*' + \
                                    'Ataque de Identidade:' + str(valor_ataque_identidade) + '*' + \
                                    'Ameaça:' + str(valor_ameaca) + '*' + \
                                    'Toxidade:' + str(valor_toxidade)

                array_metricas.append(valores_concatenados)

                #print(json.dumps(response_dict, indent=2))
            except:
                pass
        
        funcoes_auxiliares = FuncoesAuxiliares()
        funcoes_auxiliares.adiciona_nova_coluna('./dados_mensagens_aux_polaridade_e_nrc_emotions.csv', './dados_metricas.csv', 'GooglePerspectiveMetrics', array_metricas)