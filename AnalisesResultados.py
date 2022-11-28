#from leia import SentimentIntensityAnalyzer  # LeIA
from leia import *
import textstat  # Textstat - pip install textstat - para instalar
from googletrans import Translator  # GoogleTrans para tradução
import yake  # Para pegar palavras mais utilizadas
from nrclex import NRCLex  # NrcLex para análise de emoções
import pandas as pd
import numpy as np
from collections import defaultdict

from FuncoesAuxiliares import *
from GooglePerspectiveApi import *

class AnalisesResultados():
    def analisa_polaridade(self, retornoMensagens):
        s = SentimentIntensityAnalyzer()
        array_polaridade = []

        for i in range(len(retornoMensagens)):
            frase = retornoMensagens[i][1]
            if frase is not np.nan:
                retornoPolaridade = s.polarity_scores(frase)
                #print('Frase: "', frase, '" tem compound no valor de: ', retornoPolaridade['compound'])
                array_polaridade.append(retornoPolaridade['compound'])
            else:
                array_polaridade.append(np.nan)

        '''
        se compound >= 0.05   é POSITIVO
        se compound <= -0.05  é NEGATIVO
        se compound > -0.05 e compound < 0.05 é NEUTRO
        '''

        funcoes_auxiliares = FuncoesAuxiliares()
        funcoes_auxiliares.adiciona_nova_coluna('./data/dados_mensagens.csv', './data/dados_mensagens_aux_polaridade.csv', 'polaridade', array_polaridade)

    '''def analisaFacilidadeLeitura(retornoMensagens):
        textstat.set_lang('en')

        test_data = 'Frase teste que tem que ser transformada para inglês'

        translator = Translator()

        test_data = translator.translate(test_data, src='pt', dest='en')
        print('Texto traduzido: ', test_data.text)

        # Facilidade de leitura de um texto
        teste = textstat.flesch_reading_ease(test_data.text)
    
        #https://pypi.org/project/textstat/
        #90-100      Very easy
        #0-29        Very confusing
        
        print('Facilidade de leitura da frase "', test_data.text, '": ', teste)
    '''

    def analisa_nrc_lex(self, retornoMensagens):
        # TESTE API - NRCLex (emoções) e Yake (pega palavras mais usadas)

        array_emocoes_nrc = []

        #teste = ['i will abandon you', 'i am very sad', 'the life is amazing']

        for i in range(len(retornoMensagens)):
            frase = retornoMensagens[i][1]
            #'Olá a todos, Nova regra (e não acredito que tenho que dizer isso), por favor, não dê à luz no canal de voz. Isso deixa as pessoas muito desconfortáveis.' #teste[i]

            if frase is not np.nan:
                textstat.set_lang('en')
                translator = Translator()
                frase_traduzida = translator.translate(frase, src='pt', dest='en')
                #print('Texto traduzido: ', frase_traduzida.text)
                
                '''kw_extractor = yake.KeywordExtractor(lan='pt')
                keywords = kw_extractor.extract_keywords(frase)

                for kw in keywords:
                    print(kw)

                    # creating objects
                    emotion = NRCLex(kw[0])

                    # Classify emotion
                    print('\n\n', kw[0], ': ', emotion.top_emotions)'''

                #NRC-Emotion-Lexicon-v0.92/NRC-emotion-lexicon-wordlevel-alphabetized-v0.92.txt

                emotion = NRCLex(frase_traduzida.text)
                # Classify emotion
                #print('\n\n', frase, ': ', emotion.top_emotions)

                emocoes_sentenca = ''
                for i in range(len(emotion.top_emotions)):
                    nome_emocao = emotion.top_emotions[i][0]
                    valor_emocao = emotion.top_emotions[i][1]
                    if i+1 != len(emotion.top_emotions):
                        emocoes_sentenca += str(nome_emocao) + ':' + str(valor_emocao) + '*'
                    else:
                        emocoes_sentenca += str(nome_emocao) + ':' + str(valor_emocao)
                if emocoes_sentenca == '':
                    array_emocoes_nrc.append('None')
                else:
                    array_emocoes_nrc.append(emocoes_sentenca)
            else:
                array_emocoes_nrc.append(np.nan)

        funcoes_auxiliares = FuncoesAuxiliares()
        funcoes_auxiliares.adiciona_nova_coluna('./data/dados_mensagens_aux_polaridade.csv', './data/dados_mensagens_aux_polaridade_e_nrc_emotions.csv', 'NRC_EMOTIONS', array_emocoes_nrc)

    def chamada_google_perspectiveApi(self, retornoMensagens):
        chamada_google_perspective_api = GooglePerspectiveApi()
        chamada_google_perspective_api.chama_api_google_perspective(retornoMensagens)

    def classifica_mensagens(self, retornoMensagens):

        dic_classificacao = defaultdict(list)

        #Obs a mensagem[i] pode ter mais de 1 classificação

        for i in range(len(retornoMensagens)):
            polaridade = retornoMensagens[i][3] #Polaridade (valor num)
            emocoes_nrc = retornoMensagens[i][4].split('*') #Nrc emotions (Emocoes:valor*Emocoes:Valor)
            google_perspective = retornoMensagens[i][5].split('*') #Google perspective (Emocoes:valor*Emocoes*valor)

            for nrc in range(len(emocoes_nrc)):
                nome_emocao_nrc = emocoes_nrc[nrc].split(':')[0]
                valor_emocao_nrc = emocoes_nrc[nrc].split(':')[1]

                for google_p in range(len(google_perspective)):
                    nome_emocao_google = google_perspective[google_p].split(':')[0]
                    valor_emocao_google = google_perspective[google_p].split(':')[1]

                    eh_reclamacao = (nome_emocao_google == 'Toxidade' and float(valor_emocao_google) > 0.8) \
                                    | (nome_emocao_google == 'Toxidade Grave' and float(valor_emocao_google) > 0.8)

                    eh_agressao = (nome_emocao_google == 'Raiva' and float(valor_emocao_google) > 0.8) \
                                  | (nome_emocao_google == 'Ataque De Identidade' and float(valor_emocao_google) > 0.8) \
                                  | (nome_emocao_google == 'Ameaça' and float(valor_emocao_google) > 0.8) 

                    eh_elogio = (nome_emocao_google == 'Alegria' and float(valor_emocao_google) > 0.8) \
                                | (nome_emocao_nrc == 'positive' and float(valor_emocao_nrc) > 0.8)

                    eh_insatisfacao = (nome_emocao_google == 'Desgosto' and float(valor_emocao_google) > 0.8) \
                                      | (nome_emocao_google == 'Tristeza' and float(valor_emocao_google) > 0.8)

                    if float(polaridade) < 0 and eh_reclamacao:
                        if 'Reclamação' not in dic_classificacao[i]:
                            dic_classificacao[i].append('Reclamação')
                    if float(polaridade) < 0 and eh_agressao:
                        if 'Agressão' not in dic_classificacao[i]:
                            dic_classificacao[i].append('Agressão')
                    if float(polaridade) > 0 and eh_elogio:
                        if 'Elogio' not in dic_classificacao[i]:
                            dic_classificacao[i].append('Elogio')
                    if float(polaridade) < 0 and eh_insatisfacao:
                        if 'Insatisfação' not in dic_classificacao[i]:
                            dic_classificacao[i].append('Insatisfação')
                    '''if not(eh_reclamacao) and not(eh_agressao) and not(eh_elogio) and not(eh_insatisfacao):
                        dic_classificacao[i].append('None') #Erro aqui...'''
                    

                
        #Grava no csv
        funcoes_auxiliares = FuncoesAuxiliares()
        funcoes_auxiliares.adiciona_nova_coluna('./data/dados_metricas.csv', './data/dados_metricas_finais.csv', 'classificacao', dic_classificacao)
                    
    def analise_metricas(self, retornoMensagens):
        #Analise de Polaridade
        self.analisa_polaridade(retornoMensagens)

        # TESTE API - textstat e googleTrans - POR ENQUANTO N TO USANDO, ACHO Q N VAI SER RELEVANTE
        #analisaFacilidadeLeitura(retornoMensagens)

        #Atualiza a variavel contendo as mensagens
        retorno_mensagens = pd.read_csv('./data/dados_mensagens_aux_polaridade.csv', sep='-')
        
        #Analisa emoções utilizando NRCLex
        self.analisa_nrc_lex(retorno_mensagens.loc[:].values)

        retorno_mensagens = pd.read_csv('./data/dados_mensagens_aux_polaridade_e_nrc_emotions.csv', sep='-')

        # Analisa Google Perspective API
        self.chamada_google_perspectiveApi(retorno_mensagens.loc[:].values)

        # Classifica as mensagens

        retorno_mensagens = pd.read_csv('./data/dados_metricas.csv', sep='-')

        self.classifica_mensagens(retorno_mensagens.loc[:].values)
