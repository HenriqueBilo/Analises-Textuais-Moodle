import pandas as pd
import numpy as np
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.express as px
from FuncoesAuxiliares import *
import webbrowser

class GraficosMetricas():
    def formata_data(self, data):
        #2022-07-15 00:00:00
        data_formato_antigo = str(data).split(' ')[0]
        vetor_data = data_formato_antigo.split('-')
        return vetor_data[2] + '/' + vetor_data[1] + '/' + vetor_data[0]

    def formata_nrc_emotions(self, emotion):
        dicionario_retorno = {}

        if emotion != 'None':
            if '*' in emotion:
                todas_emocoes = emotion.split('*')
                for unica_emocao in todas_emocoes:
                    nome_emocao = unica_emocao.split(':')[0]
                    valor_emocao = unica_emocao.split(':')[1]

                    nome_emocao = self.traduz_emocoes_nrc(nome_emocao)

                    dicionario_retorno[nome_emocao.upper()] = valor_emocao
            else:
                nome_emocao = emotion.split(':')[0]
                valor_emocao = emotion.split(':')[1]

                nome_emocao = self.traduz_emocoes_nrc(nome_emocao)

                dicionario_retorno[nome_emocao.upper()] = valor_emocao

        return dicionario_retorno

    def traduz_emocoes_nrc(self, emocao):
        if emocao == 'fear':
            return 'Medo'
        elif emocao == 'anger':
            return 'Raiva'
        elif emocao == 'anticipation':
            return 'Antecipação'
        elif emocao == 'trust':
            return 'Confiança'
        elif emocao == 'surprise':
            return 'Surpresa'
        elif emocao == 'positive':
            return 'Positivo'
        elif emocao == 'negative':
            return 'Negativo'
        elif emocao == 'sadness':
            return 'Tristeza'
        elif emocao == 'disgust':
            return 'Desgosto'
        else:
            return 'Alegria'

    def formata_google_emotions(self, emotion):
        dicionario_retorno = {}

        if '*' in emotion:
            todas_emocoes = emotion.split('*')
            for unica_emocao in todas_emocoes:
                nome_emocao = unica_emocao.split(':')[0]

                if ' ' in nome_emocao.upper():
                    vet_emocao_formatada = nome_emocao.split(' ')
                    emocao_formatada = ''
                    for i, palavra in enumerate(vet_emocao_formatada):
                        if i == 0:
                            emocao_formatada += palavra
                        else:
                            emocao_formatada += '_' + palavra

                    valor_emocao = unica_emocao.split(':')[1]
                    dicionario_retorno[emocao_formatada] = float(valor_emocao)
                else:
                    valor_emocao = unica_emocao.split(':')[1]
                    dicionario_retorno[nome_emocao] = float(valor_emocao)
        else:
            nome_emocao = emotion.split(':')[0]

            if ' ' in nome_emocao.upper():
                vet_emocao_formatada = nome_emocao.split(' ')
                emocao_formatada = ''
                for i, palavra in enumerate(vet_emocao_formatada):
                    if i == 0 or i + 1 < len(vet_emocao_formatada):
                        emocao_formatada += palavra
                    else:
                        emocao_formatada += '_' + palavra
                valor_emocao = emotion.split(':')[1]
                dicionario_retorno[emocao_formatada] = float(valor_emocao)
            else:
                valor_emocao = emotion.split(':')[1]
                dicionario_retorno[nome_emocao] = float(valor_emocao)

        return dicionario_retorno

    def cria_grafico_metricas(self):

        #Prepara os dados

        df = pd.read_csv('./data/dados_metricas.csv', sep='-', index_col=False)

        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        df = df.sort_values(by=['data'])
        df['data'] = df['data'].map(self.formata_data)
        df = df.reset_index()
        df = df.drop(labels='index', axis=1)
        df['polaridade'] = pd.to_numeric(df['polaridade'])

        retorno_nrc_emocoes = df['NRC_EMOTIONS'].map(self.formata_nrc_emotions)
        array_nome_nrc_emocoes = []
        dict_nrc_emocoes = {}

        for dados in retorno_nrc_emocoes:
            if len(dados) != 0:
                for nrc_emocao in dados:
                    if nrc_emocao not in array_nome_nrc_emocoes:
                        array_nome_nrc_emocoes.append(nrc_emocao)
                        dict_nrc_emocoes[nrc_emocao] = []

        #Pra fechar o numero de linhas do dataframe
        while len(array_nome_nrc_emocoes) < len(df.index):
            array_nome_nrc_emocoes.append('CONFIANÇA')

        for i, dados in enumerate(retorno_nrc_emocoes):
            if len(dados) != 0:
                for nrc_emocao in dados:
                    dict_nrc_emocoes[nrc_emocao].append(float(dados[nrc_emocao]))
                for emocao in array_nome_nrc_emocoes:
                    while len(dict_nrc_emocoes[emocao]) < i + 1:
                        dict_nrc_emocoes[emocao].append(np.nan)  
            else:
                for chave in dict_nrc_emocoes.keys():
                    dict_nrc_emocoes[chave].append(np.nan)

        #TESTEEE    
        '''for chave in dict_nrc_emocoes.keys():
            while len(dict_nrc_emocoes[chave]) < 10:
                dict_nrc_emocoes[chave].append(np.nan)'''
            
        #NRC - Tratamento valores de cada emoção (1 coluna pra cada)
        for emocao_nrc in array_nome_nrc_emocoes:
            df[emocao_nrc] = dict_nrc_emocoes[emocao_nrc]   

        #NRC - Adiciona uma coluna contendo todos os nomes das emoções
        #TESTEEEE
        #data = {'NOMES_NRC_EMOCOES': array_nome_nrc_emocoes}
        #df['NOMES_NRC_EMOCOES'] = data['NOMES_NRC_EMOCOES']

        #NRC - Cria colunas para saber qual linha tem determinada emoção
        for i, linha in df.iterrows():
            if hasattr(linha, 'CONFIANÇA'):
                df.at[i,'TEM_CONFIANÇA'] = 'CONFIANÇA'
            #if linha.trust != '0':
            if hasattr(linha, 'POSITIVO'):
                #if linha.positive != '0':
                df.at[i,'TEM_POSITIVO'] = 'POSITIVO'
            if hasattr(linha, 'MEDO'):
                #if linha.fear != '0':
                df.at[i,'TEM_MEDO'] = 'MEDO'
            if hasattr(linha, 'RAIVA'):
                #if linha.anger != '0':
                df.at[i,'TEM_RAIVA'] = 'RAIVA'
            if hasattr(linha, 'ANTECIPAÇÃO'):
                #if linha.anticipation != '0':
                df.at[i,'TEM_ANTECIPAÇÃO'] = 'ANTECIPAÇÃO'
            if hasattr(linha, 'SURPRESA'):
                #if linha.surprise != '0':
                df.at[i,'TEM_SURPRESA'] = 'SURPRESA'
            if hasattr(linha, 'NEGATIVO'):
                #if linha.negative != '0':
                df.at[i,'TEM_NEGATIVO'] = 'NEGATIVO'
            if hasattr(linha, 'TRISTEZA'):
                #if linha.sadness != '0':
                df.at[i,'TEM_TRISTEZA'] = 'sadness'
            if hasattr(linha, 'DESGOSTO'):
                #if linha.disgust != '0':
                df.at[i,'TEM_DESGOSTO'] = 'DESGOSTO'
            if hasattr(linha, 'ALEGRIA'):
                #if linha.joy != '0':
                df.at[i,'TEM_ALEGRIA'] = 'ALEGRIA'

        #df = df.drop(labels='mensagem', axis=1) #Teste
        df = df.drop(labels='NRC_EMOTIONS', axis=1) #Teste
        #df = df.drop(labels='GooglePerspectiveMetrics', axis=1) #Teste

        retorno_google_emocoes = df['GooglePerspectiveMetrics'].map(self.formata_google_emotions)

        array_nome_google_emocoes = []
        dict_google_emocoes = {}

        for dados in retorno_google_emocoes:
            if len(dados) != 0:
                for google_emocao in dados:
                    if google_emocao.upper() not in array_nome_google_emocoes:
                        array_nome_google_emocoes.append(google_emocao.upper())
                        dict_google_emocoes[google_emocao.upper()] = []
                    #array_valores_aux.append(dados[nrc_emocao])

        #Pra fechar o numero de linhas do dataframe
        while len(array_nome_google_emocoes) < len(df.index):
            array_nome_google_emocoes.append('PROFANIDADE')

        for i, dados in enumerate(retorno_google_emocoes):
            if len(dados) != 0:
                for google_emocao in dados:
                    dict_google_emocoes[google_emocao.upper()].append(float(dados[google_emocao]))
                for emocao in array_nome_google_emocoes:
                    while len(dict_google_emocoes[emocao]) < i + 1:
                        dict_google_emocoes[emocao.upper()].append(np.nan)  
            else:
                for chave in dict_google_emocoes.keys():
                    dict_google_emocoes[chave.upper()].append(np.nan)
                    
        '''for chave in dict_google_emocoes.keys():
            while len(dict_google_emocoes[chave]) < 10:
                dict_google_emocoes[chave].append(np.nan)'''

        #GOOGLE_EMOTIONS - Tratamento valores de cada emoção (1 coluna pra cada)
        for emocao_google in array_nome_google_emocoes:
                df[emocao_google] = dict_google_emocoes[emocao_google]   

        #NRC - Adiciona uma coluna contendo todos os nomes das emoções
        #TESTEEEE
        #data = {'NOMES_GOOGLE_EMOCOES': array_nome_google_emocoes}
        #df['NOMES_GOOGLE_EMOCOES'] = data['NOMES_GOOGLE_EMOCOES']

        #NRC - Cria colunas para saber qual linha tem determinada emoção
        for i, linha in df.iterrows():
            if linha.AMEAÇA != '0':
                df.at[i,'TEM_AMEAÇA'] = 'AMEAÇA'
            if linha.TOXIDADE != '0':
                df.at[i,'TEM_TOXIDADE'] = 'TOXIDADE'
            if linha.PROFANIDADE != '0':
                df.at[i,'TEM_PROFANIDADE'] = 'PROFANIDADE'
            if linha.TOXIDADE_GRAVE != '0':
                df.at[i,'TEM_TOXIDADE_GRAVE'] = 'TOXIDADE_GRAVE'
            if linha.ATAQUE_DE_IDENTIDADE != '0':
                df.at[i,'TEM_ATAQUE_DE_IDENTIDADE'] = 'ATAQUE_DE_IDENTIDADE'

        #Cria dataFrame para o combo de emoções
        df_combos = pd.DataFrame()

        for i in range(len(array_nome_nrc_emocoes)):
            if array_nome_nrc_emocoes[i] not in array_nome_google_emocoes:
                array_nome_google_emocoes.append(array_nome_nrc_emocoes[i])

        data = {'EMOCOES_COMBO': array_nome_google_emocoes}
        df_combos['EMOCOES_COMBO'] = data['EMOCOES_COMBO']

        #NRC - Cria colunas para saber qual linha tem determinada emoção
        '''
        for i, linha in df.iterrows():
            if linha.trust != '0':
                df.at[i,'TEM_TRUST'] = 'trust'
            if linha.positive != '0':
                df.at[i,'TEM_POSITIVE'] = 'positive'
            if linha.fear != '0':
                df.at[i,'TEM_FEAR'] = 'fear'
            if linha.anger != '0':
                df.at[i,'TEM_ANGER'] = 'anger'
            if linha.anticipation != '0':
                df.at[i,'TEM_ANTICIPATION'] = 'anticipation'
            if linha.surprise != '0':
                df.at[i,'TEM_SURPRISE'] = 'surprise'
            if linha.negative != '0':
                df.at[i,'TEM_NEGATIVE'] = 'negative'
            if linha.sadness != '0':
                df.at[i,'TEM_SADNESS'] = 'sadness'
            if linha.disgust != '0':
                df.at[i,'TEM_DISGUST'] = 'disgust'
            if linha.joy != '0':
                df.at[i,'TEM_JOY'] = 'joy' 
        '''
    
        #print(df[:])
        #tratamentoArquivoFinal()

        app = dash.Dash(__name__)

        app.layout = html.Div([

            #Primeiro gráfico

            html.Div([
                dcc.Graph(
                figure={
                    'data': [
                        {'x': df['data'], 'y': df['polaridade'], 'type': 'bar', 'name': 'SF'},
                    ],
                    'layout': {
                        'title': 'Visualização da Métrica Polaridade por Aluno'
                    }
                },
                id='grafico_polaridade'
            )
            ],className='eight columns'),

            html.Div([
                html.Br(),
                html.Label(['Escolha um Aluno (Identificador):'],style={'font-weight': 'bold', 'text-align': 'center'}),
                dcc.Dropdown(id='cboAlunoPolaridade',
                    options=[{'label':x, 'value':x} for x in df.sort_values('idUsuario')['idUsuario'].unique()], #df['usuario'].unique()
                    value=df['idUsuario'][0] if len(df['idUsuario']) > 0 else '', #Deve ta vindo vazio dai n funciona print ("par" if x % 2 == 0 else "impar")
                    multi=False,
                    disabled=False,
                    clearable=True,
                    searchable=True,
                    placeholder='Escolha um Aluno...',
                    className='form-dropdown',
                    style={'width':"90%"},
                    persistence='string',
                    persistence_type='memory'),
            ],className='three columns'),

            #Fim primeiro gráfico

            #Segundo Gráfico

            html.Div([
                dcc.Graph(id='grafico_metricas')
            ],className='eight columns'),

            html.Div([

                html.Br(),
                html.Label(['Escolha um Aluno (Identificador):'],style={'font-weight': 'bold', 'text-align': 'center'}),
                dcc.Dropdown(id='cboAlunos',
                    options=[{'label':x, 'value':x} for x in df.sort_values('idUsuario')['idUsuario'].unique()], #df['usuario'].unique()
                    value=df['idUsuario'][0] if len(df['idUsuario']) > 0 else '',
                    multi=True,
                    disabled=False,
                    clearable=True,
                    searchable=True,
                    placeholder='Escolha um Aluno...',
                    className='form-dropdown',
                    style={'width':"90%"},
                    persistence='string',
                    persistence_type='memory'),

                dcc.Dropdown(id='cboNrcEmotion',
                    options=[{'label':x, 'value':x} for x in df_combos.sort_values('EMOCOES_COMBO')['EMOCOES_COMBO'].unique()], #df['usuario'].unique()
                    value=df_combos['EMOCOES_COMBO'][0] if len(df_combos['EMOCOES_COMBO']) > 0 else '',
                    multi=False,
                    disabled=False,
                    clearable=True,
                    searchable=True,
                    placeholder='Escolha uma Métrica...',
                    className='form-dropdown',
                    style={'width':"90%"},
                    persistence='string',
                    persistence_type='memory'),

                html.Br(),

                html.Label(['Mensagem selecionada:'],style={'font-weight': 'bold', 'text-align': 'center'}),
                dcc.Textarea(
                    id='textAreaMsgs',
                    #value='TextArea contendo a mensagem selecionada',
                    value='',
                    style={'width': '90%', 'height': 300},
                ),
        
                #Testeee
                dcc.ConfirmDialog(
                    id='alertaSemMensagens',
                    message='Não há mensagens para o curso selecionado.',
                ),

            ],className='three columns'),

            #Fim segundo gráfico
        
        ])

        @app.callback(
            Output('grafico_polaridade','figure'),
            [Input('cboAlunoPolaridade','value')]
        )

        def atualiza_grafico_polaridade(aluno):
            dff = df[df['idUsuario'] == aluno]
            #fig = px.bar(df[mask], x='data', y='polaridade', color='idUsuario')
            
            cores = []
            for polaridade in dff['polaridade']:
                if float(polaridade) >= 0:
                    cores.append('green')
                else:
                    cores.append('red')

            fig = {
                'data': 
                [
                    {'x': dff['data'], 'y': dff['polaridade'], 'type': 'bar', 'marker' : { 'color' : cores}},
                    #{'x': df['data'], 'y': df['polaridade'], 'type': 'bar', 'name': u'Montréal'},
                ],
                'layout': {
                    'title': 'Visualização da Métrica \'Polaridade\' por Aluno',
                    'xaxis': {
                        'title': 'DATA'
                    },
                    'yaxis': {
                        'title': 'POLARIDADE'
                    },
                    'font': {
                        'size': 15,
                        'x': 0.5,
                        'xanchor': 'center'
                    },
                }
            }

            return fig

        @app.callback(
            [
                Output('grafico_metricas','figure'),
                Output('textAreaMsgs', 'value'),
                Output('alertaSemMensagens', 'displayed')
            ],
            [Input('grafico_metricas', 'clickData'),
            Input('cboAlunos','value'),
            Input('cboNrcEmotion','value')]
        )

        def atualiza_grafico_metricas_nrc(clickData, alunos, nrc_emotion):
            dff_aux_alunos = ''

            if isinstance(alunos, int): #Caso for apenas um número
                dff_aux_alunos = df['idUsuario']==alunos
            else: #Caso forem múltiplas opções selecionadas
                if len(alunos) == 1: #Se tiver apenas uma opção selecionada
                    dff_aux_alunos = df['idUsuario']==alunos[0]
                else:
                    if len(alunos) == 0: #Caso nenhuma for selecionada, não exibe nada
                        alunos = 0
                        dff_aux_alunos = df['idUsuario']==alunos
                    else: #Caso tenha mais de uma, filtra
                        alunos_selecionados_df = []
                        vet_bool = []
                        for i, aluno in enumerate(alunos):
                            if i == 0:
                                vet_bool = (df['idUsuario']==aluno).values
                            else:
                                new_vet_bool = (df['idUsuario']==aluno).values
                                for indice, elem in enumerate(vet_bool):
                                    if (new_vet_bool[indice] != vet_bool[indice]) and new_vet_bool[indice] == True:
                                        vet_bool[indice] = True

                        dff_aux_alunos = vet_bool

            filtraPelaColuna = nrc_emotion
            #colorPelaColuna = 'TEM_' + nrc_emotion.upper()
            if filtraPelaColuna != '':
                dff=df[ dff_aux_alunos & (df['TEM_' + nrc_emotion.upper()]==nrc_emotion)]
                dff = dff[dff[filtraPelaColuna].notnull()]

                fig = px.line(dff, x='data', y=filtraPelaColuna, color='idUsuario', height=600) 
                #markers=True ou #text='mensagem' #Pra LINE
                #hover_data={'mensagem'}
                #scatter
                #Teste

                #fig.update_traces(marker=dict(size=12,line=dict(width=2, color='DarkSlateGrey')), selector=dict(mode='markers'))
                fig.update_traces(mode='markers+lines', opacity=1.0, marker=dict(size=12)) #textposition="bottom right" Pra caso use a tag text na line
                #opacity=0.5
                #
                
                fig.update_layout(yaxis={'title':filtraPelaColuna.upper()},
                                xaxis={'title':'DATA'},
                                title={'text':'Métricas De Cada Aluno (Teste)',
                                'font':{'size':20},'x':0.5,'xanchor':'center'},
                                hovermode='x')
                
                #Tratamento pro Click do ponto
                gValorTexto = ''
                vet_datas_mensagens_procuradas = []

                if clickData is not None:
                    for indicePoints in range(len(clickData['points'])):
                        vet_datas_mensagens_procuradas.append(clickData['points'][indicePoints]['x'])

                    vet_alunos_mensagens_verificadas = []
                    vet_mensagens_verificadas = []

                    for i, data_df in enumerate(dff['data'].values):
                        for data_mensagem_procurada in vet_datas_mensagens_procuradas:
                            if data_mensagem_procurada == data_df:
                                #dff['idUsuario'].values[i] not in vet_alunos_mensagens_verificadas and 
                                if dff['mensagem'].values[i] not in vet_mensagens_verificadas:
                                    vet_alunos_mensagens_verificadas.append(dff['idUsuario'].values[i])
                                    vet_mensagens_verificadas.append(dff['mensagem'].values[i])
                                    gValorTexto += 'Aluno ' + str(dff['idUsuario'].values[i]) + ': ' + dff['mensagem'].values[i] + '\n\n\n'
                return fig, gValorTexto, False
            else:
                return '', '', True

            #Teste Data em modo DateTime
            #dff['data'] = pd.to_datetime(dff['data'], format='%d/%m/%Y')
            #dff = dff.sort_values(by=['data'])
            #Teste

            

            
            
            

        webbrowser.open('http://127.0.0.1:8050')
        app.run_server(debug=False)

        funcoes_auxiliares = FuncoesAuxiliares()
        funcoes_auxiliares.deleta_arquivos_auxiliares()
