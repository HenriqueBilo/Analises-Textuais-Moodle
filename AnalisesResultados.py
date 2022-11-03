from leia import SentimentIntensityAnalyzer  # LeIA
import textstat  # Textstat - pip install textstat - para instalar
from googletrans import Translator  # GoogleTrans para tradução
import yake  # Para pegar palavras mais utilizadas
from nrclex import NRCLex  # NrcLex para análise de emoções
import pandas as pd

from FuncoesAuxiliares import *
from GooglePerspectiveApi import *

class AnalisesResultados():
    def analisa_polaridade(self, retornoMensagens):
        s = SentimentIntensityAnalyzer()
        array_polaridade = []

        for i in range(len(retornoMensagens)):
            frase = retornoMensagens[i][1]
            retornoPolaridade = s.polarity_scores(frase)
            #print('Frase: "', frase, '" tem compound no valor de: ', retornoPolaridade['compound'])
            array_polaridade.append(retornoPolaridade['compound'])

        '''
        se compound >= 0.05   é POSITIVO
        se compound <= -0.05  é NEGATIVO
        se compound > -0.05 e compound < 0.05 é NEUTRO
        '''

        funcoes_auxiliares = FuncoesAuxiliares()
        funcoes_auxiliares.adiciona_nova_coluna('./dados_mensagens.csv', './dados_mensagens_aux_polaridade.csv', 'polaridade', array_polaridade)

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
            frase = retornoMensagens[i][1] #teste[i]

            textstat.set_lang('en')

            #test_data = 'Frase teste que tem que ser transformada para inglês'

            translator = Translator()

            frase_traduzida = translator.translate(frase, src='pt', dest='en')
            #print('Texto traduzido: ', frase_traduzida.text)
            

            '''kw_extractor = yake.KeywordExtractor(lan='en')
            keywords = kw_extractor.extract_keywords(frase)

            for kw in keywords:
                print(kw)

                # creating objects
                emotion = NRCLex(kw[0])

                # Classify emotion
                print('\n\n', kw[0], ': ', emotion.top_emotions)'''
                    
            emotion = NRCLex(frase_traduzida.text)
            # Classify emotion
            #print('\n\n', frase, ': ', emotion.top_emotions)

            emocoes_sentenca = ''
            for i in range(len(emotion.raw_emotion_scores)):
                nome_emocao = emotion.top_emotions[i][0]
                valor_emocao = emotion.top_emotions[i][1]
                if i+1 != len(emotion.raw_emotion_scores):
                    emocoes_sentenca += str(nome_emocao) + ':' + str(valor_emocao) + '*'
                else:
                    emocoes_sentenca += str(nome_emocao) + ':' + str(valor_emocao)
            if emocoes_sentenca == '':
                array_emocoes_nrc.append('None')
            else:
                array_emocoes_nrc.append(emocoes_sentenca)

        funcoes_auxiliares = FuncoesAuxiliares()
        funcoes_auxiliares.adiciona_nova_coluna('./dados_mensagens_aux_polaridade.csv', './dados_mensagens_aux_polaridade_e_nrc_emotions.csv', 'NRC_EMOTIONS', array_emocoes_nrc)

    def chamada_google_perspectiveApi(self, retornoMensagens):
        chamada_google_perspective_api = GooglePerspectiveApi()
        chamada_google_perspective_api.chama_api_google_perspective(retornoMensagens)

    '''def tratamentoArquivoFinal():
        #df = pd.read_csv('./dados_metricas.csv', sep=';', index_col=False)

        #df['data'] = pd.to_datetime(df['data'])
        #df = df.groupby(['data','polaridade', 'idUsuario'], as_index=False)['polaridade'].mean()
        #df = df.set_index('data')
        #df = df.groupby([pd.Grouper(freq="M"),'polaridade'])['polaridade'].mean().reset_index()


        with open('./dados_metricas.csv', 'r') as read_obj, \
            open('./dados_metricas_finais.csv', 'w', newline='', encoding='utf-8') as write_obj:
            csv_reader = csv.reader(read_obj, delimiter=';', quotechar='|')
            csv_writer = csv.writer(write_obj, delimiter=';', quotechar='|')
            for i, linha in enumerate(csv_reader):
                if i == 0:
                    csv_writer.writerow([linha[0], linha[1], linha[2], linha[3], 'idmensagem', 'userid', 'message', 'data'])
                else:
                    novaLinha = linha[0] 
                    linha.append(array_valores_novos[i-1])

                csv_writer.writerow(linha)


        for linha in df['GooglePerspectiveMetrics'].values:
            metrica_e_valor = linha.split('*')
            for metrica in metrica_e_valor:
                metrica_nome = metrica.split(':')[0]
                metrica_valor = metrica.split(':')[1]'''
    
    def analise_metricas(self, retornoMensagens):
        #Analise de Polaridade
        self.analisa_polaridade(retornoMensagens)

        # TESTE API - textstat e googleTrans - POR ENQUANTO N TO USANDO, ACHO Q N VAI SER RELEVANTE
        #analisaFacilidadeLeitura(retornoMensagens)

        #Atualiza a variavel contendo as mensagens
        retorno_mensagens = pd.read_csv('./dados_mensagens_aux_polaridade.csv', sep=';')
        
        #Analisa emoções utilizando NRCLex
        self.analisa_nrc_lex(retorno_mensagens.loc[:].values)

        retorno_mensagens = pd.read_csv('./dados_mensagens_aux_polaridade_e_nrc_emotions.csv', sep=';')

        # Analisa Google Perspective API
        self.chamada_google_perspectiveApi(retorno_mensagens.loc[:].values)
        
        funcoes_auxiliares = FuncoesAuxiliares()
        funcoes_auxiliares.deleta_arquivos_auxiliares()
