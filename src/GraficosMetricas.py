import pandas as pd
import numpy as np
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.express as px
from src.FuncoesAuxiliares import *
import webbrowser
from datetime import date

class GraficosMetricas():
    def formata_data(self, data):
        data_formato_antigo = str(data).split(' ')[0]
        vetor_data = data_formato_antigo.split('-')
        return vetor_data[2] + '/' + vetor_data[1] + '/' + vetor_data[0]

    def formata_nrc_emotions(self, emotion):
        dicionario_retorno = {}

        if emotion != 'None':
            if '*' in emotion:
                todas_emocoes = emotion.split('*')
                for unica_emocao in todas_emocoes:
                    if unica_emocao != '':
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
            return 'Ansiedade'
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
            return 'Nojo'
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

        df = pd.read_csv('./data/dados_metricas_finais.csv', sep='-', index_col=False)

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
            array_nome_nrc_emocoes.append('None')

        for i, dados in enumerate(retorno_nrc_emocoes):
            if len(dados) != 0:
                for nrc_emocao in dados:
                    dict_nrc_emocoes[nrc_emocao].append(float(dados[nrc_emocao]))
                for emocao in array_nome_nrc_emocoes:
                    if emocao != 'None':
                        while len(dict_nrc_emocoes[emocao]) < i + 1:
                            dict_nrc_emocoes[emocao].append(np.nan)  
            else:
                for chave in dict_nrc_emocoes.keys():
                    dict_nrc_emocoes[chave].append(np.nan)

        #NRC - Tratamento valores de cada emoção (1 coluna pra cada)
        for emocao_nrc in array_nome_nrc_emocoes:
            if emocao_nrc != 'None':
                df[emocao_nrc] = dict_nrc_emocoes[emocao_nrc]   

        #NRC - Cria colunas para saber qual linha tem determinada emoção
        for i, linha in df.iterrows():
            if hasattr(linha, 'CONFIANÇA'):
                df.at[i,'TEM_CONFIANÇA'] = 'CONFIANÇA'
            else:
                df.at[i,'TEM_CONFIANÇA'] = 'NONE'
            if hasattr(linha, 'MEDO'):
                df.at[i,'TEM_MEDO'] = 'MEDO'
            else:
                df.at[i,'TEM_MEDO'] = 'NONE'
            if hasattr(linha, 'RAIVA'):
                df.at[i,'TEM_RAIVA'] = 'RAIVA'
            else:
                df.at[i,'TEM_RAIVA'] = 'NONE'
            if hasattr(linha, 'ANSIEDADE'):
                df.at[i,'TEM_ANSIEDADE'] = 'ANSIEDADE'
            else:
                df.at[i,'TEM_ANSIEDADE'] = 'NONE'
            if hasattr(linha, 'SURPRESA'):
                df.at[i,'TEM_SURPRESA'] = 'SURPRESA'
            else:
                df.at[i,'TEM_SURPRESA'] = 'NONE'
            if hasattr(linha, 'TRISTEZA'):
                df.at[i,'TEM_TRISTEZA'] = 'sadness'
            else:
                df.at[i,'TEM_TRISTEZA'] = 'NONE'
            if hasattr(linha, 'NOJO'):
                df.at[i,'TEM_NOJO'] = 'NOJO'
            else:
                df.at[i,'TEM_NOJO'] = 'NONE'
            if hasattr(linha, 'ALEGRIA'):
                df.at[i,'TEM_ALEGRIA'] = 'ALEGRIA'
            else:
                df.at[i,'TEM_ALEGRIA'] = 'NONE'

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
                    
        #GOOGLE_EMOTIONS - Tratamento valores de cada emoção (1 coluna pra cada)
        for emocao_google in array_nome_google_emocoes:
                df[emocao_google] = dict_google_emocoes[emocao_google]   

        #Google Perspective - Cria colunas para saber qual linha tem determinada emoção
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
            if linha.INSULTO != '0':
                df.at[i,'TEM_INSULTO'] = 'INSULTO'

        #Cria dataFrame para o combo de emoções
        df_combos = pd.DataFrame()


        #Teste

        array_nome_nrc_emocoes.append('RAIVA')
        array_nome_nrc_emocoes.append('ANSIEDADE')
        array_nome_nrc_emocoes.append('NOJO')
        array_nome_nrc_emocoes.append('MEDO')
        array_nome_nrc_emocoes.append('ALEGRIA')
        array_nome_nrc_emocoes.append('TRISTEZA')
        array_nome_nrc_emocoes.append('SURPRESA')
        array_nome_nrc_emocoes.append('CONFIANÇA')

        #Teste

        for i in range(len(array_nome_nrc_emocoes)):
            if array_nome_nrc_emocoes[i] not in array_nome_google_emocoes:
                if array_nome_nrc_emocoes[i] != 'None':
                    array_nome_google_emocoes.append(array_nome_nrc_emocoes[i])

        data = {'EMOCOES_COMBO': array_nome_google_emocoes}
        df_combos['EMOCOES_COMBO'] = data['EMOCOES_COMBO']

        #print(df[:])

        #Para utilizar no filtro de data
        if len(df['data']) > 0:
            dataInicial = df['data'][0].split('/')
            dataInicial = date(int(dataInicial[2]), int(dataInicial[1]), int(dataInicial[0]))

            dataFinal = df['data'][len(df['data']) - 1].split('/')
            dataFinal = date(int(dataFinal[2]), int(dataFinal[1]), int(dataFinal[0]))
        else:
            dataInicial = ''
            dataFinal = ''

        app = dash.Dash(
            __name__,external_stylesheets=['https://use.fontawesome.com/releases/v5.7.2/css/all.css'],

            meta_tags=[
                {'charset': 'utf-8'},
                {'name':'viewport','content':'width=device-width, initial-scale=1.0, shrink-to-fit=no'}
            ],
        )

        app.layout = html.Div([

            #Primeiro gráfico

            html.Div([

                html.Div([
                    html.I(className='far fa-address-card', style={'font-size':'36px', 'margin-left': '170%', 'margin-top': '46%'}),
                ],className='one column'),

                html.Div([
                    
                    html.Label(
                        ['Escolha o Aluno:'],
                        style={'font-weight': 'bold', 'text-align': 'left'},
                    ),
                    dcc.Dropdown(id='cboAlunoPolaridade',
                        options=[{'label':x, 'value':x} for x in df.sort_values('idUsuario')['idUsuario'].unique()], #df['usuario'].unique()
                        value=df['idUsuario'][0] if len(df['idUsuario']) > 0 else '', #Deve ta vindo vazio dai n funciona print ("par" if x % 2 == 0 else "impar")
                        multi=False,
                        disabled=False,
                        clearable=True,
                        searchable=True,
                        placeholder='Escolha o Aluno...',
                        className='form-dropdown',
                        style={'width':"90%"},
                        persistence='string',
                        persistence_type='memory'),
                ],className='two columns margin-Left'),

                html.Div([
                    html.I(className='far fa-calendar-check', style={'font-size':'36px', 'margin-left': '140%', 'margin-top': '46%'}),
                ],className='one column'),

                html.Div([
                    html.Label(['Escolha o período:'],style={'font-weight': 'bold', 'text-align': 'left'}),
                    dcc.DatePickerRange(
                        id="dateRangePolaridade",
                        min_date_allowed='',
                        max_date_allowed='',
                        start_date=dataInicial,
                        end_date=dataFinal,
                        display_format='DD/MM/YYYY'
                    ),
                ],className='four columns padding-1P'),

            ],className='twelve columns div-fields'),

            html.Div([
                html.Br(),
                dcc.Graph(id='grafico_polaridade')
            ],className='eight columns'),

            html.Div([
                html.Label(['Mensagem selecionada:'],style={'font-weight': 'bold', 'text-align': 'center'}),
                html.Div(
                    id='textAreaMsgsPolaridade',
                    style={'width': '95%', 'height': '450px', 'min-width': '120px', 'min-height': '90px', 'max-width': '400px', 'max-height': '470px', 'padding': '1px', 'border': '1px solid rgb(169, 169, 169)', 'overflow-y': 'auto', 'resize': 'both', 'background-color': 'rgb(235, 235, 228)' },
                ),
            ],className='three columns margin-Top'),

            html.Div([
                html.Br()
            ], className='twelve columns border-bottom'),

            #Fim primeiro gráfico

            #Segundo Gráfico

            html.Div([

                html.Div([
                    html.I(className='far fa-address-card', style={'font-size':'36px', 'margin-left': '170%', 'margin-top': '46%'}),
                ],className='one column'),

                html.Div([
                    
                    html.Label(
                        ['Escolha o(s) Aluno(s):'],
                        style={'font-weight': 'bold', 'text-align': 'left'},
                    ),
                    dcc.Dropdown(id='cboAlunos',
                        options=[{'label':x, 'value':x} for x in df.sort_values('idUsuario')['idUsuario'].unique()], #df['usuario'].unique()
                        value=df['idUsuario'][0] if len(df['idUsuario']) > 0 else '',
                        multi=True,
                        disabled=False,
                        clearable=True,
                        searchable=True,
                        placeholder='Escolha o(s) Aluno(s)...',
                        className='form-dropdown',
                        style={'width':'90%'},
                        persistence='string',
                        persistence_type='memory'),
                ],className='two columns margin-Left'),

                html.Div([
                    html.I(className='far fa-calendar-check', style={'font-size':'36px', 'margin-left': '140%', 'margin-top': '46%'}),
                ],className='one column'),

                html.Div([
                    html.Label(['Escolha o período:'],style={'font-weight': 'bold', 'text-align': 'left'}),
                    dcc.DatePickerRange(
                        id="dateRangeMetricas",
                        min_date_allowed='',
                        max_date_allowed='',
                        start_date=dataInicial,
                        end_date=dataFinal,
                        display_format='DD/MM/YYYY',
                    ),
                ],className='three columns fake padding-1P'),

                html.Div([
                    html.I(className='far fa-smile', style={'font-size':'36px', 'margin-left': '170%', 'margin-top': '46%'}),
                ],className='one column'),

                html.Div([
                    html.Label(['Escolha uma métrica:'],style={'font-weight': 'bold', 'text-align': 'left'}),
                    dcc.Dropdown(id='cboMetricas',
                        options=[{'label':x, 'value':x} for x in df_combos.sort_values('EMOCOES_COMBO')['EMOCOES_COMBO'].unique()], #df['usuario'].unique()
                        value=df_combos['EMOCOES_COMBO'][0] if len(df_combos['EMOCOES_COMBO']) > 0 else '',
                        multi=False,
                        disabled=False,
                        clearable=True,
                        searchable=True,
                        placeholder='Escolha uma Métrica...',
                        className='form-dropdown',
                        style={'width':"100%"},
                        persistence='string',
                        persistence_type='memory'),
                ],className='two columns fake margin-Left'),

                

            ],className='twelve columns div-fields'),

            html.Div([
                html.Br(),
                dcc.Graph(id='grafico_metricas')
            ],className='eight columns'),

            html.Div([
                html.Label(['Mensagem selecionada:'],style={'font-weight': 'bold', 'text-align': 'center'}),
                html.Div(
                    id='divMetricasFakeTextArea', 
                    style={'width': '95%', 'height': '470px', 'min-width': '120px', 'min-height': '90px', 'max-width': '400px', 'max-height': '470px', 'padding': '1px', 'border': '1px solid rgb(169, 169, 169)', 'overflow-y': 'auto', 'resize': 'both', 'background-color': 'rgb(235, 235, 228)' }
                ),
            ],className='three columns margin-Top'),

            html.Div([
                dcc.ConfirmDialog(
                    id='alertaSemMensagens',
                    message='Não há mensagens para o curso selecionado.',
                ),
            ])

            #Fim segundo gráfico
        
        ])

        @app.callback(
            [
                Output('grafico_polaridade','figure'),
                Output('textAreaMsgsPolaridade', 'children'),
            ],
            [
                Input('grafico_polaridade', 'clickData'),
                Input('cboAlunoPolaridade','value'),
                Input('dateRangePolaridade', 'start_date'),
                Input('dateRangePolaridade', 'end_date'),
                State('textAreaMsgsPolaridade', 'children')
            ]
        )

        def atualiza_grafico_polaridade(clickData, aluno, start_date, end_date, children):
            df_date = pd.DataFrame()
            df_date['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
            df_date = df_date.sort_values(by=['data'])

            dff = df[(df['idUsuario'] == aluno) & (df_date['data'] >= start_date) & (df_date['data'] <= end_date)]
            
            if len(dff['polaridade']) > 0:
                cores = []
                for polaridade in dff['polaridade']:
                    if float(polaridade) >= 0:
                        cores.append('green')
                    else:
                        cores.append('red')

                #dff['cores_polaridade'] = cores
                dff.insert(2, 'cores_polaridade', cores, True)

                fig = px.bar(dff, x=dff['data'], y=dff['polaridade'], 
                    color=dff['cores_polaridade'],
                    color_discrete_map={
                        'green': 'green',
                        'red': 'red'
                    },
                    labels=dict(data="DATA", polaridade="POLARIDADE"),
                    title='Visualização da Métrica \'Polaridade\' por Aluno', 
                    height=600)

                fig.update_layout(title_text='Visualização da Métrica \'Polaridade\' por Aluno', title_x=0.5)

                fig.update_layout({
                    'showlegend':False,
                })

                #Tratamento pro Click do ponto
                gValorTexto = ''
                gCabecalhoTexto = ''
                gStringClassificacao = ''
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
                                    classificacoes = dff['classificacao'].values[i].split(',')
                                    gStringClassificacao = ''
                                    b_tem_classificacao = False
                                    for j in range(len(classificacoes)):
                                        classificacao = classificacoes[j][1:].replace("'", "").upper()
                                        if(classificacao != ']'):
                                            b_tem_classificacao = True
                                            gStringClassificacao += '[' + classificacao.replace(']', '') + ']'

                                    if len(vet_mensagens_verificadas) <= 1:
                                        if b_tem_classificacao:
                                            gCabecalhoTexto = 'ALUNO ' + str(dff['idUsuario'].values[i]) + ': ' # + string_de_classificacao + ': '
                                        else:
                                            gCabecalhoTexto = 'ALUNO ' + str(dff['idUsuario'].values[i]) + ': '

                                    if len(vet_mensagens_verificadas) > 1:
                                        gValorTexto += '&nbsp;&nbsp;' + dff['mensagem'].values[i] 
                                    else:
                                        gValorTexto += dff['mensagem'].values[i]
                
                corClassificacao = ''
                indices_adicionados_classificacao_children = []

                if gStringClassificacao != '':
                    vetClassificacao = gStringClassificacao.split(']')
                    for i in range(len(vetClassificacao)):
                        if vetClassificacao[i] != '':
                            vetClassificacao[i] += ']'
                            if vetClassificacao[i] == '[AGRESSÃO]':
                                corClassificacao = 'red'
                            elif vetClassificacao[i] == '[RECLAMAÇÃO]' or vetClassificacao[i] == '[INSATISFAÇÃO]':
                                corClassificacao = 'orange'
                            elif vetClassificacao[i] == '[ELOGIO]':
                                corClassificacao = 'green'
                            elif vetClassificacao[i] == '[PREOCUPAÇÃO]':
                                corClassificacao = 'purple'
                            else:
                                corClassificacao = 'black'

                            nova_div = html.Div(
                                children=[
                                    html.Div(vetClassificacao[i], style={'color': corClassificacao, 'float': 'left'})
                                ]
                            )

                            indices_adicionados_classificacao_children.append(len(children))
                            children.append(nova_div)

                conteudo_classificacao = {}
                if len(indices_adicionados_classificacao_children) > 0:
                    for i in range(len(indices_adicionados_classificacao_children)):
                        if i == 0:
                            teste = children[indices_adicionados_classificacao_children[i]]
                        else:
                            teste.children.append(children[indices_adicionados_classificacao_children[i]])
                    conteudo_classificacao = teste

                indices_mensagens_adicionadas_children = [] #Zera os indices
                if '&nbsp;&nbsp;' in gValorTexto: #Se tem que quebrar linha entre as mensagens
                    gValorTexto = gValorTexto.split('&nbsp;&nbsp;')
                    for frase_selecionada in range(len(gValorTexto)):
                        indice_dataFrame_mensagem = dff[dff['mensagem'] == gValorTexto[frase_selecionada]].index.values.astype(int)[0]
                        classificacao_mensagem_atual = dff['classificacao'][indice_dataFrame_mensagem]
                        gStringClassificacao = ''

                        classificacoes = classificacao_mensagem_atual.split(',')
                        for j in range(len(classificacoes)):
                            classificacao = classificacoes[j][1:].replace("'", "").upper()
                            if(classificacao != ']'):
                                gStringClassificacao += '[' + classificacao.replace(']','') + ']'

                        if gStringClassificacao != '':
                            vetClassificacao = gStringClassificacao.split(']')
                            for i in range(len(vetClassificacao)):
                                if vetClassificacao[i] != '':
                                    vetClassificacao[i] += ']'
                                    if vetClassificacao[i] == '[AGRESSÃO]':
                                        corClassificacao = 'red'
                                    elif vetClassificacao[i] == '[RECLAMAÇÃO]' or vetClassificacao[i] == '[INSATISFAÇÃO]':
                                        corClassificacao = 'orange'
                                    elif vetClassificacao[i] == '[ELOGIO]':
                                        corClassificacao = 'green'
                                    elif vetClassificacao[i] == '[PREOCUPAÇÃO]':
                                        corClassificacao = 'purple'
                                    else:
                                        corClassificacao = 'black'

                                    nova_div_classificacao = html.Div(
                                        children=[
                                            html.Div(vetClassificacao[i], style={'color': corClassificacao, 'float': 'left'})
                                        ]
                                    )
                            div_separando_mensagens = html.Div(
                                children=[
                                    html.Div(gCabecalhoTexto, style={'color': 'black', 'font-weight': 'bold','float': 'left'}),
                                    nova_div_classificacao,
                                    html.Br(),
                                    html.Div(gValorTexto[frase_selecionada], style={})
                                ]
                            )

                            indices_mensagens_adicionadas_children.append(len(children))
                            children.append(div_separando_mensagens)
                        else:
                            div_separando_mensagens = html.Div(
                                children=[
                                    html.Div(gCabecalhoTexto, style={'color': 'black', 'font-weight': 'bold','float': 'left'}),
                                    html.Br(),
                                    html.Div(gValorTexto[frase_selecionada], style={})
                                ]
                            )

                            indices_mensagens_adicionadas_children.append(len(children))
                            children.append(div_separando_mensagens)

                conteudo_mensagem_mesmo_usuario = {}
                if len(indices_mensagens_adicionadas_children) > 0:
                    for i in range(len(indices_mensagens_adicionadas_children)):
                        if i == 0:
                            teste = children[indices_mensagens_adicionadas_children[i]]
                        else:
                            teste.children.append(children[indices_mensagens_adicionadas_children[i]])
                    conteudo_mensagem_mesmo_usuario = teste

                if len(indices_mensagens_adicionadas_children) > 0 : #Tratamento para caso de múltiplas mensagens de um mesmo usuário
                    #html.Div(gCabecalhoTexto, style={'color': 'black', 'font-weight': 'bold','float': 'left'}),
                    #html.Div(conteudo_classificacao),
                    #html.Br(),
                    new_div = html.Div(
                        children=[
                            html.Div(conteudo_mensagem_mesmo_usuario, style={}),
                            html.Br(),
                        ]
                    )

                else:
                    new_div = html.Div(
                        children=[
                            html.Div(gCabecalhoTexto, style={'color': 'black', 'font-weight': 'bold','float': 'left'}),
                            html.Div(conteudo_classificacao),
                            html.Br(),
                            html.Div(gValorTexto, style={}),
                            html.Br(),
                        ]
                    )

                return fig, new_div.children
            else:
                return '', ''

        @app.callback(
            [
                Output('grafico_metricas','figure'),
                Output('alertaSemMensagens', 'displayed'),
                Output('divMetricasFakeTextArea', 'children'),
            ],
            [
                Input('grafico_metricas', 'clickData'),
                Input('cboAlunos','value'),
                Input('cboMetricas','value'),
                Input('dateRangeMetricas', 'start_date'),
                Input('dateRangeMetricas', 'end_date'),
                State('divMetricasFakeTextArea', 'children')
            ]
        )

        def atualiza_grafico_metricas(clickData, alunos, nrc_emotion, start_date, end_date, children):
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
            if filtraPelaColuna != '':
                df_date = pd.DataFrame()
                df_date['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
                df_date = df_date.sort_values(by=['data'])
                
                if nrc_emotion == None:
                    dff=df[dff_aux_alunos & (df_date['data'] >= start_date) & (df_date['data'] <= end_date)]
                else:
                    dff=df[dff_aux_alunos & (df['TEM_' + nrc_emotion.upper()]==nrc_emotion) & (df_date['data'] >= start_date) & (df_date['data'] <= end_date)]


                b_mostra_legenda = True
                if filtraPelaColuna in dff.columns:
                    dff = dff[dff[filtraPelaColuna].notnull()]
                else:
                    dff = pd.DataFrame()
                    dff['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
                    dff = dff.sort_values(by=['data'])
                    dff[filtraPelaColuna] = None
                    dff['idUsuario'] = None
                    b_mostra_legenda = False

                fig = px.line(dff, 
                    x='data', 
                    y=filtraPelaColuna, 
                    color='idUsuario', 
                    labels=dict(idUsuario="USUÁRIO(S)"),
                    height=600) 

                fig.update_traces(mode='markers+lines', opacity=1.0, marker=dict(size=12)) #textposition="bottom right" Pra caso use a tag text na line

                fig.update_layout(yaxis={'title':filtraPelaColuna.upper()},
                                xaxis={'title':'DATA'},
                                title={'text':'Visualização Métricas Gerais',
                                'font':{'size':20},'x':0.5,'xanchor':'center'},
                                hovermode='x')

                if not b_mostra_legenda:
                    fig.update_layout({
                        'showlegend':False,
                    })

                #Tratamento pro Click do ponto
                gValorTexto = ''
                gCabecalhoTexto = ''
                gStringClassificacao = ''
                vet_datas_mensagens_procuradas = []

                if clickData is not None:
                    for indicePoints in range(len(clickData['points'])):
                        vet_datas_mensagens_procuradas.append(clickData['points'][indicePoints]['x'])

                    vet_alunos_mensagens_verificadas = []
                    vet_mensagens_verificadas = []

                    for i, data_df in enumerate(dff['data'].values):
                        for data_mensagem_procurada in vet_datas_mensagens_procuradas:
                            if data_mensagem_procurada == data_df:
                                if dff['mensagem'].values[i] not in vet_mensagens_verificadas:
                                    vet_alunos_mensagens_verificadas.append(dff['idUsuario'].values[i])
                                    vet_mensagens_verificadas.append(dff['mensagem'].values[i])
                                    
                                    classificacoes = dff['classificacao'].values[i].split(',')
                                    gStringClassificacao = ''
                                    b_tem_classificacao = False
                                    for j in range(len(classificacoes)):
                                        classificacao = classificacoes[j][1:].replace("'", "").upper()
                                        if(classificacao != ']'):
                                            b_tem_classificacao = True
                                            gStringClassificacao += '[' + classificacao.replace(']','') + ']'

                                    if len(vet_mensagens_verificadas) <= 1:
                                        if b_tem_classificacao:
                                            gCabecalhoTexto = 'ALUNO ' + str(dff['idUsuario'].values[i]) + ': ' #' ' + gStringClassificacao +
                                        else:
                                            gCabecalhoTexto = 'ALUNO ' + str(dff['idUsuario'].values[i]) + ': '

                                    if len(vet_mensagens_verificadas) > 1:
                                        gValorTexto += '&nbsp;&nbsp;' + dff['mensagem'].values[i] 
                                    else:
                                        gValorTexto += dff['mensagem'].values[i]
                                    #
          
                corClassificacao = ''
                indices_adicionados_classificacao_children = []
                #dict_divs = defaultdict(list)

                if gStringClassificacao != '':
                    vetClassificacao = gStringClassificacao.split(']')
                    for i in range(len(vetClassificacao)):
                        if vetClassificacao[i] != '':
                            vetClassificacao[i] += ']'
                            if vetClassificacao[i] == '[AGRESSÃO]':
                                corClassificacao = 'red'
                            elif vetClassificacao[i] == '[RECLAMAÇÃO]' or vetClassificacao[i] == '[INSATISFAÇÃO]':
                                corClassificacao = 'orange'
                            elif vetClassificacao[i] == '[ELOGIO]':
                                corClassificacao = 'green'
                            elif vetClassificacao[i] == '[PREOCUPAÇÃO]':
                                corClassificacao = 'purple'
                            else:
                                corClassificacao = 'black'

                            nova_div = html.Div(
                                children=[
                                    html.Div(vetClassificacao[i], style={'color': corClassificacao, 'float': 'left'})
                                ]
                            )

                            indices_adicionados_classificacao_children.append(len(children))
                            children.append(nova_div)

                conteudo_classificacao = {}
                if len(indices_adicionados_classificacao_children) > 0:
                    for i in range(len(indices_adicionados_classificacao_children)):
                        if i == 0:
                            teste = children[indices_adicionados_classificacao_children[i]]
                        else:
                            teste.children.append(children[indices_adicionados_classificacao_children[i]])
                    conteudo_classificacao = teste

                indices_mensagens_adicionadas_children = [] #Zera os indices
                if '&nbsp;&nbsp;' in gValorTexto: #Se tem que quebrar linha entre as mensagens
                    gValorTexto = gValorTexto.split('&nbsp;&nbsp;')
                    for frase_selecionada in range(len(gValorTexto)):
                        indice_dataFrame_mensagem = dff[dff['mensagem'] == gValorTexto[frase_selecionada]].index.values.astype(int)[0]
                        classificacao_mensagem_atual = dff['classificacao'][indice_dataFrame_mensagem]
                        gStringClassificacao = ''

                        classificacoes = classificacao_mensagem_atual.split(',')
                        for j in range(len(classificacoes)):
                            classificacao = classificacoes[j][1:].replace("'", "").upper()
                            if(classificacao != ']'):
                                gStringClassificacao += '[' + classificacao.replace(']','') + ']'

                        if gStringClassificacao != '':
                            vetClassificacao = gStringClassificacao.split(']')
                            for i in range(len(vetClassificacao)):
                                if vetClassificacao[i] != '':
                                    vetClassificacao[i] += ']'
                                    if vetClassificacao[i] == '[AGRESSÃO]':
                                        corClassificacao = 'red'
                                    elif vetClassificacao[i] == '[RECLAMAÇÃO]' or vetClassificacao[i] == '[INSATISFAÇÃO]':
                                        corClassificacao = 'orange'
                                    elif vetClassificacao[i] == '[ELOGIO]':
                                        corClassificacao = 'green'
                                    elif vetClassificacao[i] == '[PREOCUPAÇÃO]':
                                        corClassificacao = 'purple'
                                    else:
                                        corClassificacao = 'black'

                                    nova_div_classificacao = html.Div(
                                        children=[
                                            html.Div(vetClassificacao[i], style={'color': corClassificacao, 'float': 'left'})
                                        ]
                                    )
                            div_separando_mensagens = html.Div(
                                children=[
                                    html.Div(gCabecalhoTexto, style={'color': 'black', 'font-weight': 'bold','float': 'left'}),
                                    nova_div_classificacao,
                                    html.Br(),
                                    html.Div(gValorTexto[frase_selecionada], style={})
                                ]
                            )

                            indices_mensagens_adicionadas_children.append(len(children))
                            children.append(div_separando_mensagens)
                        else:
                            div_separando_mensagens = html.Div(
                                children=[
                                    html.Div(gCabecalhoTexto, style={'color': 'black', 'font-weight': 'bold','float': 'left'}),
                                    html.Br(),
                                    html.Div(gValorTexto[frase_selecionada], style={})
                                ]
                            )

                            indices_mensagens_adicionadas_children.append(len(children))
                            children.append(div_separando_mensagens)

                
                conteudo_mensagem_mesmo_usuario = {}
                if len(indices_mensagens_adicionadas_children) > 0:
                    for i in range(len(indices_mensagens_adicionadas_children)):
                        if i == 0:
                            teste = children[indices_mensagens_adicionadas_children[i]]
                        else:
                            teste.children.append(children[indices_mensagens_adicionadas_children[i]])
                    conteudo_mensagem_mesmo_usuario = teste

                if len(indices_mensagens_adicionadas_children) > 0 : #Tratamento para caso de múltiplas mensagens de um mesmo usuário
                    #html.Div(gCabecalhoTexto, style={'color': 'black', 'font-weight': 'bold','float': 'left'}),
                    #html.Div(conteudo_classificacao),
                    #html.Br(),
                    new_div = html.Div(
                        children=[
                            html.Div(conteudo_mensagem_mesmo_usuario, style={}),
                            html.Br(),
                        ]
                    )

                else:
                    new_div = html.Div(
                        children=[
                            html.Div(gCabecalhoTexto, style={'color': 'black', 'font-weight': 'bold','float': 'left'}),
                            html.Div(conteudo_classificacao),
                            html.Br(),
                            html.Div(gValorTexto, style={}),
                            html.Br(),
                        ]
                    )


                return fig, False, new_div.children
            else:
                return '', True, '' 

        webbrowser.open('http://127.0.0.1:8050')
        app.run_server(debug=False)
