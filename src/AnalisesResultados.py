from src.FuncoesAuxiliares import *
from src.GooglePerspectiveApi import *

from leia import SentimentIntensityAnalyzer  # LeIA
import textstat 
from googletrans import Translator  # GoogleTrans para tradução
from yake import KeywordExtractor # Para pegar palavras mais utilizadas
from nrclex import NRCLex  # NrcLex para análise de emoções
from pandas import read_csv as pd_read_csv
from numpy import nan
from collections import defaultdict, OrderedDict
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger, CRITICAL

environ['AUTOGRAPH_VERBOSITY'] = '3'
environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
getLogger("tensorflow").setLevel(CRITICAL)

from unidecode import unidecode
from transformers import logging as lg_transformers, RobertaTokenizerFast, TFRobertaForSequenceClassification, pipeline, BertConfig
lg_transformers.set_verbosity(50)

class AnalisesResultados():
    def analisa_polaridade(self, retornoMensagens):
        s = SentimentIntensityAnalyzer()
        array_polaridade = []

        for i in range(len(retornoMensagens)):
            frase = retornoMensagens[i][1].replace('\\', '\\\\')

            if frase is not nan:
                retornoPolaridade = s.polarity_scores(frase)
                array_polaridade.append(retornoPolaridade['compound'])
            else:
                array_polaridade.append(nan)

        funcoes_auxiliares = FuncoesAuxiliares()
        funcoes_auxiliares.adiciona_nova_coluna('./data/dados_mensagens.csv', './data/dados_mensagens_aux_polaridade.csv', 'polaridade', array_polaridade)

    def tratamento_thread_nrc_lex(self, frase, indice_frase, dict_emocoes_nrc, lock):
        if frase is not nan:
            textstat.set_lang('en')
            translator = Translator()

            frase = unidecode(frase)
            frase_traduzida = translator.translate(frase, src='pt', dest='en')
            frase_traduzida.text = frase_traduzida.text.replace('\u200b', '')
            emotion = NRCLex(frase_traduzida.text)

            emocoes_sentenca = ''

            lista_emocoes_repetidas = ['anger', 'disgust', 'fear', 'joy', 'surprise', 'sadness']

            for i in range(len(emotion.top_emotions)):
                nome_emocao = emotion.top_emotions[i][0]
                valor_emocao = emotion.top_emotions[i][1]
                if nome_emocao != 'positive' and nome_emocao != 'negative' and (nome_emocao not in lista_emocoes_repetidas):
                    if nome_emocao == 'anticip':
                        nome_emocao = 'anticipation'
                    if i+1 != len(emotion.top_emotions):
                        emocoes_sentenca += str(nome_emocao) + ':' + str(valor_emocao) + '*'
                    else:
                        emocoes_sentenca += str(nome_emocao) + ':' + str(valor_emocao)
            
            if emocoes_sentenca == '':
                dict_emocoes_nrc[indice_frase] = 'None'
            else:
                dict_emocoes_nrc[indice_frase] = emocoes_sentenca

            lock.acquire()
            self.contador_global += 1
            self.funcoes_auxiliares.barra_progresso(self.contador_global, self.tamanho_mensagens, 'Analisando')
            lock.release()
        else:
            dict_emocoes_nrc[frase] = nan

            lock.acquire()
            self.contador_global += 1
            self.funcoes_auxiliares.barra_progresso(self.contador_global + 1, self.tamanho_mensagens, 'Analisando')
            lock.release()
            
    def analisa_nrc_lex(self, retornoMensagens):
        dict_emocoes_nrc = {}
        self.contador_global = 0
        self.funcoes_auxiliares = FuncoesAuxiliares()
        self.tamanho_mensagens = len(retornoMensagens)

        pool = ThreadPoolExecutor()
        lock = Lock()

        for i in range(len(retornoMensagens)): #Percorre todas mensagens
            frase = retornoMensagens[i][1].replace('\\', '\\\\')
            pool.submit(self.tratamento_thread_nrc_lex, frase, i+1, dict_emocoes_nrc, lock) #Primeiro parametro é a função e os outros são os parametros pra função
            
        pool.shutdown(wait=True)
        print()

        dict_emocoes_nrc_ordenado = OrderedDict(sorted(dict_emocoes_nrc.items()))
        self.funcoes_auxiliares.adiciona_nova_coluna_dict('./data/dados_mensagens_aux_polaridade.csv', './data/dados_mensagens_aux_polaridade_e_nrc_emotions.csv', 'NRC_EMOTIONS', dict_emocoes_nrc_ordenado)

    def chamada_google_perspectiveApi(self, retornoMensagens):
        chamada_google_perspective_api = GooglePerspectiveApi()
        chamada_google_perspective_api.chama_api_google_perspective(retornoMensagens)

    def classifica_mensagens(self, retornoMensagens):

        dic_classificacao = defaultdict(list)
        funcoes_auxiliares = FuncoesAuxiliares()

        for i in range(len(retornoMensagens)):
            polaridade = retornoMensagens[i][3] #Polaridade (valor num)
            emocoes_nrc = retornoMensagens[i][4].split('*') #Nrc emotions (Emocoes:valor*Emocoes:Valor)
            emocoes_emo_roberta = retornoMensagens[i][5].split('*') #Emo Roberta (Emocoes:valor*Emocoes*valor)
            google_perspective = retornoMensagens[i][6].split('*') #Google perspective (Emocoes:valor*Emocoes*valor)

            for google_p in range(len(google_perspective)):
                nome_emocao_google = google_perspective[google_p].split(':')[0]
                valor_emocao_google = google_perspective[google_p].split(':')[1]

                eh_reclamacao, eh_agressao = self.classificador_google_perspective(nome_emocao_google, valor_emocao_google)

                if float(polaridade) < 0 and eh_reclamacao:
                    if 'Reclamação' not in dic_classificacao[i]:
                        dic_classificacao[i].append('Reclamação')
                if float(polaridade) < 0 and eh_agressao:
                    if 'Agressão' not in dic_classificacao[i]:
                        dic_classificacao[i].append('Agressão')

            eh_preocupacao = False
            eh_interesse = False

            for nrc in range(len(emocoes_nrc)):
                if emocoes_nrc[nrc] != 'None' and emocoes_nrc[nrc] != None and emocoes_nrc[nrc] != '':
                    nome_emocao_nrc = emocoes_nrc[nrc].split(':')[0]
                    valor_emocao_nrc = emocoes_nrc[nrc].split(':')[1]

                    eh_preocupacao, eh_interesse = self.classificador_emocoes_nrc(nome_emocao_nrc, valor_emocao_nrc)
            
                    if eh_preocupacao:
                        if 'Preocupação' not in dic_classificacao[i]:
                            dic_classificacao[i].append('Preocupação')

                    if eh_interesse:
                        if 'Interesse' not in dic_classificacao[i]:
                            dic_classificacao[i].append('Interesse')

            for emo_roberta in range(len(emocoes_emo_roberta)):
                nome_emo_roberta = emocoes_emo_roberta[emo_roberta].split(':')[0]
                valor_emo_roberta = emocoes_emo_roberta[emo_roberta].split(':')[1]

                eh_interesse, eh_reclamacao, eh_elogio, eh_insatisfacao, eh_preocupacao = self.classificador_emo_roberta(nome_emo_roberta, valor_emo_roberta)
            
                if float(polaridade) < 0 and eh_reclamacao:
                    if 'Reclamação' not in dic_classificacao[i]:
                        dic_classificacao[i].append('Reclamação')
                if float(polaridade) > 0 and eh_elogio:
                    if 'Elogio' not in dic_classificacao[i]:
                        dic_classificacao[i].append('Elogio')
                if float(polaridade) < 0 and eh_insatisfacao:
                    if 'Insatisfação' not in dic_classificacao[i]:
                        dic_classificacao[i].append('Insatisfação')
                if float(polaridade) > 0 and eh_interesse:
                    if 'Interesse' not in dic_classificacao[i]:
                        dic_classificacao[i].append('Interesse')
                if eh_preocupacao:
                    if 'Preocupação' not in dic_classificacao[i]:
                        dic_classificacao[i].append('Preocupação')
 
            funcoes_auxiliares.barra_progresso(i + 1, len(retornoMensagens), 'Finalizando')

        print()          
        #Grava no csv
        funcoes_auxiliares.adiciona_nova_coluna('./data/dados_metricas.csv', './data/dados_metricas_finais.csv', 'classificacao', dic_classificacao)

    def classificador_emocoes_nrc(self, nome_emocao_nrc, valor_emocao_nrc):
        
        eh_preocupacao = (nome_emocao_nrc == 'anticipation' and float(valor_emocao_nrc) > 0.7)
        eh_interesse = (nome_emocao_nrc == 'trust' and float(valor_emocao_nrc) > 0.7)

        return eh_preocupacao, eh_interesse
    
    def classificador_google_perspective(self, nome_emocao_google, valor_emocao_google):
        eh_reclamacao = (nome_emocao_google == 'Toxicidade' and float(valor_emocao_google) > 0.7) \
                        |   (nome_emocao_google == 'Toxicidade Severa' and float(valor_emocao_google) > 0.7)

        eh_agressao = (nome_emocao_google == 'Ameaça' and float(valor_emocao_google) > 0.7) \
                    | (nome_emocao_google == 'Insulto' and float(valor_emocao_google) > 0.7) \
                    | (nome_emocao_google == 'Profanidade' and float(valor_emocao_google) > 0.7) \
                    | (nome_emocao_google == 'Ataque de Identidade' and float(valor_emocao_google) > 0.7)

        return eh_reclamacao, eh_agressao

    def classificador_emo_roberta(self, nome_emo_roberta, valor_emo_roberta):
        
        eh_interesse = (nome_emo_roberta == 'curiosity' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'desire' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'excitement' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'joy' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'optimism' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'realization' and float(valor_emo_roberta) > 0.7)

        eh_reclamacao = (nome_emo_roberta == 'annoyance' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'anger' and float(valor_emo_roberta) > 0.7)

        eh_elogio = (nome_emo_roberta == 'admiration' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'approval' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'gratitude' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'love' and float(valor_emo_roberta) > 0.7)
        
        eh_insatisfacao = (nome_emo_roberta == 'disappointment' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'confusion' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'disapproval' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'disgust' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'embarrassment' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'grief' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'sadness' and float(valor_emo_roberta) > 0.7)

        eh_preocupacao = (nome_emo_roberta == 'fear' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'nervousness' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'relief' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'remorse' and float(valor_emo_roberta) > 0.7) \
                        | (nome_emo_roberta == 'caring' and float(valor_emo_roberta) > 0.7)

        return eh_interesse, eh_reclamacao, eh_elogio, eh_insatisfacao, eh_preocupacao

    def analisa_emo_roberta(self, retornoMensagens):
        dict_emocoes_emo_roberta = {}

        config = BertConfig.from_pretrained('./models--arpanghoshal--EmoRoBERTa/config.json')
        tokenizer = RobertaTokenizerFast.from_pretrained('./models--arpanghoshal--EmoRoBERTa/')
        model = TFRobertaForSequenceClassification.from_pretrained('./models--arpanghoshal--EmoRoBERTa/tf_model.h5', config=config)

        emotion_call = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer, top_k= None)

        pool = ThreadPoolExecutor()
        lock = Lock()

        self.contador_global = 0
        self.tamanho_mensagens = len(retornoMensagens)

        for i in range(len(retornoMensagens)):
            frase = retornoMensagens[i][1].replace('\\', '\\\\')  
            pool.submit(self.tratamento_thread_emo_roberta, frase, i+1, dict_emocoes_emo_roberta, lock, emotion_call) #Primeiro parametro é a função e os outros são os parametros pra função

        pool.shutdown(wait=True)
        print()

        dict_emocoes_emo_roberta_ordenado = OrderedDict(sorted(dict_emocoes_emo_roberta.items()))
        self.funcoes_auxiliares.adiciona_nova_coluna_dict('./data/dados_mensagens_aux_polaridade_e_nrc_emotions.csv', './data/dados_mensagens_aux_polaridade_e_emo_roberta_emocoes.csv', 'EMO_ROBERTA', dict_emocoes_emo_roberta_ordenado)
    
    def tratamento_thread_emo_roberta(self, frase, indice_frase, dict_emocoes_emo_roberta, lock, emotion_call):
        if frase is not nan:
            try:
                textstat.set_lang('en')
                translator = Translator()
                
                frase = unidecode(frase).encode('utf-8').decode('ascii')
                frase_traduzida = translator.translate(frase, src='pt', dest='en')
                frase_traduzida.text = frase_traduzida.text.replace('\u200b', '')
                frase_traduzida.text = frase_traduzida.text.encode('utf-8').decode('ascii')

                emocoes_sentenca = ''

                if len(frase) > 2000:
                    mensagem_dividida = frase_traduzida.text.split('.')
                    frase_palavras_chave = ''

                    for mensagem in mensagem_dividida:
                        kw_extractor = KeywordExtractor(lan='en', n=10, top=50, dedupLim=0.1, stopwords='./StopwordsList/stopwords_en.txt') #, windowsSize=3, 
                        keywords = kw_extractor.extract_keywords(mensagem)
                        
                        for palavra_ou_frase, pontuacao in keywords:
                            palavra_ou_frase_vet = palavra_ou_frase.split(' ')
                            for palavra in palavra_ou_frase_vet:
                                if palavra not in frase_palavras_chave:
                                    frase_palavras_chave += palavra + " "
                    
                    frase_traduzida.text = frase_palavras_chave

                emotion_labels = emotion_call(frase_traduzida.text)

                for index, emotion in enumerate(emotion_labels[0]):
                    nome_emocao = emotion['label']
                    valor_emocao = emotion['score']

                    if index+1 != len(emotion_labels[0]):
                        if float(valor_emocao) > 0.1:
                            emocoes_sentenca += str(nome_emocao) + ':' + str(valor_emocao) + '*'
                    else:
                        if float(valor_emocao) > 0.1:
                            emocoes_sentenca += str(nome_emocao) + ':' + str(valor_emocao)
                        else:
                            if emocoes_sentenca != '':
                                ultimo_caractere = emocoes_sentenca[-1]
                                if ultimo_caractere == '*':
                                    emocoes_sentenca = emocoes_sentenca[:-1] + ''

                dict_emocoes_emo_roberta[indice_frase] = emocoes_sentenca

                lock.acquire()
                self.contador_global += 1
                self.funcoes_auxiliares.barra_progresso(self.contador_global, self.tamanho_mensagens, 'Agregando')
                lock.release()
            except Exception as erro:
                print(erro)
                
    def analise_metricas(self, retornoMensagens):
        #Analise de Polaridade
        self.analisa_polaridade(retornoMensagens)

        #Atualiza a variavel contendo as mensagens
        retorno_mensagens = pd_read_csv('./data/dados_mensagens_aux_polaridade.csv', sep='-')
        
        #Analisa emoções utilizando NRCLex
        self.analisa_nrc_lex(retorno_mensagens.loc[:].values)

        retorno_mensagens = pd_read_csv('./data/dados_mensagens_aux_polaridade_e_nrc_emotions.csv', sep='-')
        self.analisa_emo_roberta(retorno_mensagens.loc[:].values)

        retorno_mensagens = pd_read_csv('./data/dados_mensagens_aux_polaridade_e_emo_roberta_emocoes.csv', sep='-')

        # Analisa Google Perspective API
        self.chamada_google_perspectiveApi(retorno_mensagens.loc[:].values)

        # Classifica as mensagens

        retorno_mensagens = pd_read_csv('./data/dados_metricas.csv', sep='-')

        self.classifica_mensagens(retorno_mensagens.loc[:].values)
