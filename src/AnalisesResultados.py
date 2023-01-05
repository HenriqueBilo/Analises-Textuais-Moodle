#from leia import SentimentIntensityAnalyzer  # LeIA
from leia import *
import textstat  # Textstat - pip install textstat - para instalar
from googletrans import Translator  # GoogleTrans para tradução
import yake  # Para pegar palavras mais utilizadas
from nrclex import NRCLex  # NrcLex para análise de emoções
import pandas as pd
import numpy as np
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import collections
#import timeit

from src.FuncoesAuxiliares import *
from src.GooglePerspectiveApi import *

class AnalisesResultados():
    def analisa_polaridade(self, retornoMensagens):
        s = SentimentIntensityAnalyzer()
        array_polaridade = []

        for i in range(len(retornoMensagens)):
            frase = retornoMensagens[i][1].replace('\\', '\\\\')
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

    def teste(self, frase, indice_frase, dict_emocoes_nrc, lock):
        if frase is not np.nan:
            textstat.set_lang('en')
            translator = Translator()
            frase_traduzida = translator.translate(frase, src='pt', dest='en') #Traduz para inglês

            emotion = NRCLex(frase_traduzida.text) #Obter classificação


            '''kw_extractor = yake.KeywordExtractor(lan='pt')
            keywords = kw_extractor.extract_keywords(frase)
            for kw in keywords:
                print(kw)
                # creating objects
                palavra_traduzida = translator.translate(kw[0], src='pt', dest='en') #Traduz para inglês
                emotion_kw = NRCLex(palavra_traduzida.text)
                # Classify emotion
                print('\n\n', palavra_traduzida, ': ', emotion_kw.top_emotions)'''


            emocoes_sentenca = ''
            for i in range(len(emotion.top_emotions)): #Percorre todas classificações (umas 10)
                nome_emocao = emotion.top_emotions[i][0]
                valor_emocao = emotion.top_emotions[i][1]
                if nome_emocao != 'positive' and nome_emocao != 'negative':
                    if i+1 != len(emotion.top_emotions):
                        emocoes_sentenca += str(nome_emocao) + ':' + str(valor_emocao) + '*'
                    else:
                        emocoes_sentenca += str(nome_emocao) + ':' + str(valor_emocao)
            if emocoes_sentenca == '':
                #return 'None'
                dict_emocoes_nrc[indice_frase] = 'None'
            else:
                #return emocoes_sentenca
                dict_emocoes_nrc[indice_frase] = emocoes_sentenca
                #array_emocoes_nrc.append(emocoes_sentenca)

            lock.acquire()
            self.contador_global += 1
            self.funcoes_auxiliares.barra_progresso(self.contador_global, self.tamanho_mensagens, 'Analisando')
            lock.release()

        else:
            #return np.nan
            dict_emocoes_nrc[frase] = np.nan

            lock.acquire()
            self.contador_global += 1
            self.funcoes_auxiliares.barra_progresso(self.contador_global + 1, self.tamanho_mensagens, 'Analisando')
            lock.release()
            

    def analisa_nrc_lex(self, retornoMensagens):
        # TESTE API - NRCLex (emoções) e Yake (pega palavras mais usadas)

        dict_emocoes_nrc = {}
        self.contador_global = 0
        self.funcoes_auxiliares = FuncoesAuxiliares()
        self.tamanho_mensagens = len(retornoMensagens)

        pool = ThreadPoolExecutor()
        lock = Lock()

        #with ThreadPoolExecutor() as executor:
        for i in range(len(retornoMensagens)): #Percorre todas mensagens
            frase = retornoMensagens[i][1].replace('\\', '\\\\')

            #self.teste(frase, i+1, dict_emocoes_nrc)

            pool.submit(self.teste, frase, i+1, dict_emocoes_nrc, lock) #Primeiro parametro é a função e os outros são os parametros pra função
            #time.sleep(0.1)

        pool.shutdown(wait=True)
        print()

        dict_emocoes_nrc_ordenado = collections.OrderedDict(sorted(dict_emocoes_nrc.items()))
        self.funcoes_auxiliares.adiciona_nova_coluna_dict('./data/dados_mensagens_aux_polaridade.csv', './data/dados_mensagens_aux_polaridade_e_nrc_emotions.csv', 'NRC_EMOTIONS', dict_emocoes_nrc_ordenado)

    def chamada_google_perspectiveApi(self, retornoMensagens):
        chamada_google_perspective_api = GooglePerspectiveApi()
        chamada_google_perspective_api.chama_api_google_perspective(retornoMensagens)

    def classifica_mensagens(self, retornoMensagens):

        dic_classificacao = defaultdict(list)
        funcoes_auxiliares = FuncoesAuxiliares()

        #Obs a mensagem[i] pode ter mais de 1 classificação

        for i in range(len(retornoMensagens)):
            polaridade = retornoMensagens[i][3] #Polaridade (valor num)
            emocoes_nrc = retornoMensagens[i][4].split('*') #Nrc emotions (Emocoes:valor*Emocoes:Valor)
            google_perspective = retornoMensagens[i][5].split('*') #Google perspective (Emocoes:valor*Emocoes*valor)

            for google_p in range(len(google_perspective)):
                nome_emocao_google = google_perspective[google_p].split(':')[0]
                valor_emocao_google = google_perspective[google_p].split(':')[1]

                eh_preocupacao = False
                for nrc in range(len(emocoes_nrc)):
                    if emocoes_nrc[nrc] != 'None' and emocoes_nrc[nrc] != None and emocoes_nrc[nrc] != '':
                        nome_emocao_nrc = emocoes_nrc[nrc].split(':')[0]
                        valor_emocao_nrc = emocoes_nrc[nrc].split(':')[1]

                        eh_preocupacao = self.classificador_nrc_e_google_perspective(nome_emocao_nrc, valor_emocao_nrc, nome_emocao_google, valor_emocao_google)
                
                        if eh_preocupacao:
                            if 'Preocupação' not in dic_classificacao[i]:
                                dic_classificacao[i].append('Preocupação')

                eh_reclamacao, eh_agressao, eh_elogio, eh_insatisfacao = self.classificador_google_perspective(nome_emocao_google, valor_emocao_google)
                        
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

            funcoes_auxiliares.barra_progresso(i + 1, len(retornoMensagens), 'Finalizando')

        print()          
        #Grava no csv
        funcoes_auxiliares.adiciona_nova_coluna('./data/dados_metricas.csv', './data/dados_metricas_finais.csv', 'classificacao', dic_classificacao)

    def classificador_nrc_e_google_perspective(self, nome_emocao_nrc, valor_emocao_nrc, nome_emocao_google, valor_emocao_google):
        
        eh_preocupacao = (nome_emocao_nrc == 'anticipation' and float(valor_emocao_nrc) > 0.7) \
                        | (nome_emocao_nrc == 'fear' and float(valor_emocao_nrc) > 0.7) \
                        | (nome_emocao_nrc == 'sadness' and float(valor_emocao_nrc) > 0.7)

        return eh_preocupacao
    
    def classificador_google_perspective(self, nome_emocao_google, valor_emocao_google):
        eh_reclamacao = (nome_emocao_google == 'Media_A_T' and float(valor_emocao_google) > 0.7) \
                        |   (nome_emocao_google == 'Toxicidade Severa' and float(valor_emocao_google) > 0.7)

        eh_agressao = (nome_emocao_google == 'Raiva' and float(valor_emocao_google) > 0.7) \
                    | (nome_emocao_google == 'Media_A_T' and float(valor_emocao_google) > 0.7) \
                    | (nome_emocao_google == 'Media_A_I' and float(valor_emocao_google) > 0.7) 

        eh_elogio = (nome_emocao_google == 'Alegria' and float(valor_emocao_google) > 0.7) #\
                    #| (nome_emocao_nrc == 'positive' and float(valor_emocao_nrc) > 0.2)

        eh_insatisfacao = (nome_emocao_google == 'Desgosto' and float(valor_emocao_google) > 0.7) \
                        | (nome_emocao_google == 'Tristeza' and float(valor_emocao_google) > 0.7)

        return eh_reclamacao, eh_agressao, eh_elogio, eh_insatisfacao
                 
    def analise_metricas(self, retornoMensagens):
        #Analise de Polaridade
        self.analisa_polaridade(retornoMensagens)

        # TESTE API - textstat e googleTrans - POR ENQUANTO N TO USANDO, ACHO Q N VAI SER RELEVANTE
        #analisaFacilidadeLeitura(retornoMensagens)

        #Atualiza a variavel contendo as mensagens
        retorno_mensagens = pd.read_csv('./data/dados_mensagens_aux_polaridade.csv', sep='-')
        
        #start_nrc = timeit.default_timer()

        #Analisa emoções utilizando NRCLex
        self.analisa_nrc_lex(retorno_mensagens.loc[:].values)

        #end_nrc = timeit.default_timer()

        #print('Tempo NRC: ' + str(end_nrc-start_nrc))

        retorno_mensagens = pd.read_csv('./data/dados_mensagens_aux_polaridade_e_nrc_emotions.csv', sep='-')

        #start_google = timeit.default_timer()

        # Analisa Google Perspective API
        self.chamada_google_perspectiveApi(retorno_mensagens.loc[:].values)

        #end_google = timeit.default_timer()

        #print('Tempo GOOGLE: ' + str(end_google-start_google))

        # Classifica as mensagens

        retorno_mensagens = pd.read_csv('./data/dados_metricas.csv', sep='-')

        self.classifica_mensagens(retorno_mensagens.loc[:].values)
