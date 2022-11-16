#from leia import SentimentIntensityAnalyzer  # LeIA
from leia import *
import textstat  # Textstat - pip install textstat - para instalar
from googletrans import Translator  # GoogleTrans para tradução
import yake  # Para pegar palavras mais utilizadas
from nrclex import NRCLex  # NrcLex para análise de emoções
import pandas as pd
import numpy as np

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
