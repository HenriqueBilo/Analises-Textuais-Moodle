from pickle import FALSE
from bs4 import BeautifulSoup
from matplotlib.axis import XAxis
from requests import get, post, request
import csv
import os
import pandas as pd
from datetime import datetime

from tangled_up_in_unicode import uppercase

from leia import SentimentIntensityAnalyzer  # LeIA

import textstat  # Textstat - pip install textstat - para instalar

from googletrans import Translator  # GoogleTrans para tradução

import yake  # Para pegar palavras mais utilizadas
from nrclex import NRCLex  # NrcLex para análise de emoções

import json  # Para google perspectiva api

#Imports para graficos
#import datetime
import numpy as np
import plotly.offline as py
import plotly.graph_objects as go
#from ipywidgets import widgets
import ipywidgets as widgets

#Testes
import plotly
import plotly.express as px

import dash
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output, State

import webbrowser

import plotly.graph_objs as go

# Module variables to connect to moodle api
KEY = "" 
URL = "http://localhost"  # "https://moodle.site.com"
ENDPOINT = "/webservice/rest/server.php"


def rest_api_parameters(in_args, prefix='', out_dict=None):
    """Transform dictionary/array structure to a flat dictionary, with key names
    defining the structure.
    Example usage:
    >>> rest_api_parameters({'courses':[{'id':1,'name': 'course1'}]})
    {'courses[0][id]':1,
     'courses[0][name]':'course1'}
    """
    if out_dict == None:
        out_dict = {}
    if not type(in_args) in (list, dict):
        out_dict[prefix] = in_args
        return out_dict
    if prefix == '':
        prefix = prefix + '{0}'
    else:
        prefix = prefix + '[{0}]'
    if type(in_args) == list:
        for idx, item in enumerate(in_args):
            rest_api_parameters(item, prefix.format(idx), out_dict)
    elif type(in_args) == dict:
        for key, item in in_args.items():
            rest_api_parameters(item, prefix.format(key), out_dict)
    return out_dict

def call(fname, **kwargs):
    """Calls moodle API function with function name fname and keyword arguments.
    Example:
    >>> call_mdl_function('core_course_update_courses',
                           courses = [{'id': 1, 'fullname': 'My favorite course'}])
    """
    parameters = rest_api_parameters(kwargs)
    parameters.update(
        {"wstoken": KEY, 'moodlewsrestformat': 'json', "wsfunction": fname})
    response = post(URL+ENDPOINT, parameters)
    response = response.json()
    if type(response) == dict and response.get('exception'):
        raise SystemError("Error calling Moodle API\n", response)
    return response

class CourseList():
    '''Classe que pega todos os cursos que um determinado usuário participa'''

    def __init__(self):
        self.courses = {}

    def buscaCursoPorUsuario(self, idUsuario):
        dados_cursos = call('core_enrol_get_users_courses', userid=idUsuario)
        self.grava_csv_dados_cursos(dados_cursos)
        for dados in dados_cursos:
            # VERIFICAR depois se isso funciona 100%
            if dados['progress'] == None:
                self.courses[dados['id']] = dados['displayname']

    def grava_csv_dados_cursos(self, dados_cursos):
        with open('./dados_cursos.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='|')
            writer.writerow(['id', 'nome', 'categoria'])

            for curso in dados_cursos:
                if curso['progress'] == None:
                    writer.writerow(
                        [curso['id'], curso['fullname'], curso['category']])

class Users():
    def __init__(self, course, idUsuarioBuscado):
        "Pega os usuários de um curso específico"
        users_data = call('core_enrol_get_enrolled_users', courseid=course)
        self.idUsuarioBuscado = idUsuarioBuscado
        self.users = {}
        for data in users_data:
            self.users[data['id']] = data['fullname']
        self.grava_csv_usuario(users_data)

    def grava_csv_usuario(self, infos_usuario):
        with open('./dados_usuario.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='|')
            writer.writerow(['id', 'nome', 'email', 'professor'])

            for usuario in infos_usuario:
                # if usuario['id'] == self.idUsuarioBuscado:
                # Verificar com o Wives essa validação
                cargoNoCurso = usuario['roles'][0]['shortname']
                if cargoNoCurso == 'editingteacher' or cargoNoCurso == 'teacher' or cargoNoCurso == 'professor':
                    writer.writerow(
                        [usuario['id'], usuario['fullname'], usuario['email'], 'Sim'])
                else:
                    writer.writerow(
                        [usuario['id'], usuario['fullname'], usuario['email'], 'Nao'])

class Forums():
    '''Retorna uma lista de foruns'''

    def __init__(self, arrayForums):
        forums_data = call('mod_forum_get_forums_by_courses',
                           courseids=arrayForums)
        self.forums = {}
        for forum in forums_data:
            self.forums[forum['id']] = str(
                forum['course']) + '*' + forum['name'] + '*' + forum['intro']
        self.grava_csv_forums()

    def grava_csv_forums(self):
        with open('./dados_foruns.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='|')
            writer.writerow(['id', 'course', 'name', 'intro'])

            for forum in self.forums:
                idForum = forum
                dados_foruns = self.forums[forum]
                dados_foruns = dados_foruns.split('*')

                writer.writerow([idForum, dados_foruns[0],
                                dados_foruns[1], dados_foruns[2]])

class Discussions():
    '''Retorna uma lista de discussões de um determinado fórum'''

    def __init__(self, forumId):
        discussions_data = call(
            'mod_forum_get_forum_discussions', forumid=forumId)
        self.discussions = {}
        for discussion in discussions_data['discussions']:
            soup = BeautifulSoup(discussion['message'], 'html.parser')
            self.discussions[discussion['discussion']] = discussion['name'] + \
                '*' + discussion['subject'] + '*' + soup.get_text()
        self.grava_csv_discussions()

    def grava_csv_discussions(self):
        with open('./dados_discussions.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='|')
            writer.writerow(['id', 'name', 'subject', 'message'])

            for discussion in self.discussions:
                idDiscussion = discussion
                dados_discussions = self.discussions[discussion]
                dados_discussions = dados_discussions.split('*')

                writer.writerow([idDiscussion, dados_discussions[0],
                                dados_discussions[1], dados_discussions[2]])

class Posts():
    '''Retorna a lista de posts de uma determinada discussão'''

    def __init__(self, discussionId):
        posts_data = call('mod_forum_get_discussion_posts',
                          discussionid=discussionId)
        self.posts = {}
        for post in posts_data['posts']:
            dataMensagemChatObject = datetime.fromtimestamp(post['timecreated'])
            dataFormatada = str(dataMensagemChatObject.day).zfill(2) + '/' + str(dataMensagemChatObject.month).zfill(2) + '/' + str(dataMensagemChatObject.year)

            soup = BeautifulSoup(post['message'], 'html.parser')
            self.posts[post['id']] = post['subject'] + '*' + \
                soup.get_text() + '*' + str(post['author']['id']) + '*' + dataFormatada
        self.grava_csv_posts()

    def grava_csv_posts(self):
        with open('./dados_posts.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='|')
            writer.writerow(['id', 'subject', 'message', 'autor', 'data'])

            for post in self.posts:
                idPost = post
                dados_posts = self.posts[post]
                dados_posts = dados_posts.split('*')

                writer.writerow(
                    [idPost, dados_posts[0], dados_posts[1], dados_posts[2], dados_posts[3]])

class Chats():

    def __init__(self, courseArrays):

        self.chat_messages = {}

        chats_data = call('mod_chat_get_chats_by_courses',
                          courseids=courseArrays)
        self.grava_csv_dados_chats(chats_data)
        self.chats = {}
        for chat in chats_data['chats']:
            self.chats[chat['id']] = chat['name']

    def get_messages_from_chat_id(self, chatId):
        dados_sessoes = call('mod_chat_get_sessions', chatid=chatId, showall=1)

        for sessao in dados_sessoes['sessions']:
            if len(sessao['sessionusers']) > 0:
                mensagens_sessoes = call('mod_chat_get_session_messages', chatid=chatId, sessionstart=sessao['sessionstart'], sessionend=sessao['sessionend'])
                for mensagem in mensagens_sessoes['messages']:
                    # Da pra pegar o 'userid' tbm

                    conteudoMensagem = mensagem['message']
                    if conteudoMensagem != 'enter' and conteudoMensagem != 'exit':
                        dataMensagemChatObject = datetime.fromtimestamp(mensagem['timestamp'])
                        dataFormatada = str(dataMensagemChatObject.day).zfill(2) + '/' + str(dataMensagemChatObject.month).zfill(2) + '/' + str(dataMensagemChatObject.year)

                        self.chat_messages[mensagem['id']] = conteudoMensagem + \
                            '*' + str(mensagem['chatid']) + \
                            '*' + str(mensagem['userid']) + \
                            '*' + dataFormatada

        self.reescreve_csv_dados_chat_com_mensagens()

    def grava_csv_dados_chats(self, dados_chats):
        with open('./dados_chats.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='|')
            writer.writerow(['idchat', 'course', 'namechat', 'section'])

            for chat in dados_chats['chats']:
                writer.writerow([chat['id'], chat['course'],
                                chat['name'], chat['section']])

    def reescreve_csv_dados_chat_com_mensagens(self):
        with open('./dados_chats.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            with open('./dados_chats_mensagens.csv', 'w', newline='', encoding='utf-8') as csvfilewrite:
                writer = csv.writer(csvfilewrite, delimiter=';', quotechar='|')

                for i, linha in enumerate(reader):
                    if i == 0:
                        # cabeçalho
                        #print("Cabeçalho: " + str(linha))
                        writer.writerow(
                            [linha[0], linha[1], linha[2], linha[3], 'idmensagem', 'userid', 'message', 'data'])
                    else:
                        # valores
                        #print("Valores: " + str(linha))
                        for mensagem in self.chat_messages:
                            idMensagem = mensagem
                            dados_mensagem = self.chat_messages[idMensagem]
                            dados_mensagem = dados_mensagem.split('*')
                            #idChat = chat_mensagem
                            conteudoMensagem = dados_mensagem[0]
                            mensagemChatId = dados_mensagem[1]
                            userId = dados_mensagem[2]
                            data = dados_mensagem[3]
                            if conteudoMensagem != 'enter' and conteudoMensagem != 'exit':
                                if int(mensagemChatId) == int(linha[0]):
                                    writer.writerow(
                                        [linha[0], linha[1], linha[2], linha[3], idMensagem, userId, conteudoMensagem, data])

class Autenticacao():

    def __init__(self, email):
        self.emailArray = email

    def login(self):
        infos_usuario = call('core_user_get_users_by_field',
                             field='email', values=self.emailArray)
        return infos_usuario[0]['id']

class LeituraCsvs():
    def __init__(self):
        self.dados_usuario = pd.read_csv('./dados_usuario.csv', sep=';')
        self.dados_posts = pd.read_csv('./dados_posts.csv', sep=';')
        self.dados_mensagens_diretas = pd.read_csv(
            './dados_mensagens_diretas.csv', sep=';')
        self.dados_foruns = pd.read_csv('./dados_foruns.csv', sep=';')
        self.dados_discussions = pd.read_csv(
            './dados_discussions.csv', sep=';')
        self.dados_cursos = pd.read_csv('./dados_cursos.csv', sep=';')
        self.dados_chats_mensagens = pd.read_csv(
            './dados_chats_mensagens.csv', sep=';')

    def get_dados_usuario(self):
        return self.dados_usuario

    def get_dados_posts(self):
        return self.dados_posts

    def get_dados_mensagens_diretas(self):
        return self.dados_mensagens_diretas

    def get_dados_foruns(self):
        return self.dados_foruns

    def get_dados_discussions(self):
        return self.dados_discussions

    def get_dados_cursos(self):
        return self.dados_cursos

    def get_dados_chats_mensagens(self):
        return self.dados_chats_mensagens

# Funções auxiliares

def pegaInformacoesUsuario():
    usuario = input('Informe seu usuário: ')

    emailArray = []
    emailArray.append(usuario)
    realizaLogin = Autenticacao(emailArray)
    idUsuarioBuscado = realizaLogin.login()

    listaCursosUsuario = CourseList()
    listaCursosUsuario.buscaCursoPorUsuario(idUsuarioBuscado)
    return listaCursosUsuario, idUsuarioBuscado

def menuSelecaoCurso(listaCursosUsuario):
    print('Selecione a disciplina desejada: \n')
    contadorDisciplina = 0
    dicionarioDisciplinas = {}
    for curso in listaCursosUsuario.courses:
        contadorDisciplina = contadorDisciplina + 1
        dicionarioDisciplinas[contadorDisciplina] = listaCursosUsuario.courses[curso] + \
            ' * ' + str(curso)
        print(str(contadorDisciplina) + ' - ' +
              listaCursosUsuario.courses[curso])

    disciplinaEscolhida = input()
    nomeDisciplinaEscolhida = dicionarioDisciplinas[int(disciplinaEscolhida)]
    idDisciplinaEscolhida = int(nomeDisciplinaEscolhida.split('*')[1])
    return idDisciplinaEscolhida

def coletaMensagensChatDoCurso(idDisciplinaEscolhida):
    cursosArray = []
    cursosArray.append(idDisciplinaEscolhida)

    #chatsArray = []
    retorno = Chats(cursosArray)
    for chat in retorno.chats:
        retorno.get_messages_from_chat_id(chat)
    os.remove('./dados_chats.csv')

    '''print('\nMensagens dos chats do curso: \n')
    for mensagem in retorno.chat_messages:
    print(retorno.chat_messages[int(mensagem)])'''

    return cursosArray

def coletaMensagensDiretasAoProfessor(cursosArray, idUsuarioBuscado):
    usersArray = []
    for curso in cursosArray:
        retorno = Users(curso, idUsuarioBuscado)
        usersArray.append(retorno.users)

    directMessagesArray = {}
    for user in usersArray:
        for userId in user:
            if userId == idUsuarioBuscado:
                retorno = call('core_message_get_messages', useridto=userId,
                               useridfrom=0, type='conversations', read=2)

                for msg in retorno['messages']:
                    if msg['useridfrom'] in user and msg['useridto'] in user:
                        dataMensagemChatObject = datetime.fromtimestamp(msg['timecreated'])
                        dataFormatada = str(dataMensagemChatObject.day).zfill(2) + '/' + str(dataMensagemChatObject.month).zfill(2) + '/' + str(dataMensagemChatObject.year)

                        directMessagesArray[msg['id']] = str(
                            msg['useridfrom']) + '*' + str(msg['useridto']) + '*' + msg['fullmessage'] + '*' + dataFormatada
                        # directMessagesArray.append(msg['fullmessage'])

    with open('./dados_mensagens_diretas.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='|')
        writer.writerow(['idmensagemdireta', 'useridfrom',
                        'useridto', 'fullmessage', 'data'])

        for mensagem_direta in directMessagesArray:
            idMensagemDireta = mensagem_direta
            dadosMensagem = directMessagesArray[idMensagemDireta].split('*')
            writer.writerow([idMensagemDireta, dadosMensagem[0],
                            dadosMensagem[1], dadosMensagem[2], dadosMensagem[3]])

    '''print('\nMensagens diretas dos integrantes do curso: \n')
    for msg in directMessagesArray:
        print(directMessagesArray[msg])'''

def coletaMensagensDosForuns(cursosArray):
    listaDeForums = Forums(cursosArray)

    discussionsArray = []
    for forum in listaDeForums.forums:
        forum = listaDeForums.forums[forum].split('*')
        retorno = Discussions(forum[0])
        discussionsArray.append(retorno.discussions)

    postsArray = []
    for discussion in discussionsArray:
        for discussionId in discussion:
            retorno = Posts(discussionId)
            postsArray.append(retorno.posts)

    '''print('\nMensagens dos fóruns do curso: \n')
    for post in postsArray:
        for t in post:
            soup = BeautifulSoup(post[t], 'html.parser')
            print(soup.get_text())'''

def chamaApiGooglePerspective(retornoMensagens):
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
    
    adicionaNovaColuna('./dados_mensagens_aux_polaridade_e_nrc_emotions.csv', './dados_metricas.csv', 'GooglePerspectiveMetrics', array_metricas)
  
def gravaCsvUnico(retornoMensagensChats, retornoMensagensDiretas, retornoMensagensPostsForuns):
    with open('./dados_mensagens.csv', 'w', newline='', encoding='utf-8') as csvfilewrite:
        writer = csv.writer(csvfilewrite, delimiter=';', quotechar='|')
        writer.writerow(['idUsuario', 'mensagem', 'data'])

        for msgChat in retornoMensagensChats:
            writer.writerow([msgChat[5], msgChat[6],msgChat[7]])

        for msgDireta in retornoMensagensDiretas:
            writer.writerow([msgDireta[1], msgDireta[3],msgDireta[4]])

        for msgPost in retornoMensagensPostsForuns:
            writer.writerow([msgPost[3], msgPost[2],msgPost[4]])

def deletaArquivosAuxiliares():
    #Deleta arquivos auxiliares

    array_arquivos_deletar = ['./dados_chats_mensagens.csv', './dados_cursos.csv', './dados_discussions.csv', './dados_foruns.csv', 
                             './dados_mensagens_diretas.csv', './dados_posts.csv', './dados_usuario.csv', './dados_mensagens_aux_polaridade_e_nrc_emotions.csv',
                             './dados_mensagens_aux_polaridade.csv', './dados_mensagens.csv']

    for arquivo in array_arquivos_deletar:
        if os.path.isfile(arquivo):
            os.remove(arquivo)

#Funções para Análise das Mensagens - Obtendo as Métricas

def analisaPolaridade(retornoMensagens):
    s = SentimentIntensityAnalyzer()
    array_polaridade = []

    for i in range(len(retornoMensagens)):
        frase = retornoMensagens[i][1]
        retornoPolaridade = s.polarity_scores(frase)
        #print('Frase: "', frase, '" tem compound no valor de: ', retornoPolaridade['compound'])
        array_polaridade.append(retornoPolaridade['compound'])

    '''print('Teste individual: ')

    testeRetornoS = s.polarity_scores('Eu não gosto de você, te odeio! :@')
    print('Frase: "Eu não gosto de você, te odeio! :@" tem compound no valor de: ',
          testeRetornoS['compound'])

    testeRetornoS = s.polarity_scores('Você é muito legal! <3')
    print('Frase: "Você é muito legal! <3" tem compound no valor de: ',
          testeRetornoS['compound'])'''

    '''
    se compound >= 0.05   é POSITIVO
    se compound <= -0.05  é NEGATIVO
    se compound > -0.05 e compound < 0.05 é NEUTRO
    '''
    adicionaNovaColuna('./dados_mensagens.csv', './dados_mensagens_aux_polaridade.csv', 'polaridade', array_polaridade)

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

def analisaNRCLex(retornoMensagens):
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

    adicionaNovaColuna('./dados_mensagens_aux_polaridade.csv', './dados_mensagens_aux_polaridade_e_nrc_emotions.csv', 'NRC_EMOTIONS', array_emocoes_nrc)


    '''text = ['hate', 'lovely', 'person', 'worst']

    for i in range(len(text)):
        # creating objects
        emotion = NRCLex(text[i])

        # Classify emotion
        print('\n\n', text[i], ': ', emotion.top_emotions)'''

    '''text = "Life is better when you're laughing"
    kw_extractor = yake.KeywordExtractor(lan='en')
    keywords = kw_extractor.extract_keywords(text)
    for kw in keywords:
        print(kw)

        # creating objects
        emotion = NRCLex(kw[0])

        # Classify emotion
        print('\n\n', kw[0], ': ', emotion.top_emotions)'''

def analisaGooglePerspectiveApi(retornoMensagens):
    chamaApiGooglePerspective(retornoMensagens)

def adicionaNovaColuna(input_file, output_file, coluna_nova, array_valores_novos):
    with open(input_file, 'r') as read_obj, \
        open(output_file, 'w', newline='', encoding='utf-8') as write_obj:
        csv_reader = csv.reader(read_obj, delimiter=';', quotechar='|')
        csv_writer = csv.writer(write_obj, delimiter=';', quotechar='|')
        for i, linha in enumerate(csv_reader):
            if i == 0:
                linha.append(coluna_nova)
            else:
                linha.append(array_valores_novos[i-1])

            csv_writer.writerow(linha)

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

    
def analiseMetricas(retornoMensagens):
    #Analise de Polaridade
    analisaPolaridade(retornoMensagens)

    # TESTE API - textstat e googleTrans - POR ENQUANTO N TO USANDO, ACHO Q N VAI SER RELEVANTE
    #analisaFacilidadeLeitura(retornoMensagens)

    #Atualiza a variavel contendo as mensagens
    retornoMensagens = pd.read_csv('./dados_mensagens_aux_polaridade.csv', sep=';')
    
    #Analisa emoções utilizando NRCLex
    analisaNRCLex(retornoMensagens.loc[:].values)

    retornoMensagens = pd.read_csv('./dados_mensagens_aux_polaridade_e_nrc_emotions.csv', sep=';')

    # Analisa Google Perspective API
    analisaGooglePerspectiveApi(retornoMensagens.loc[:].values)
    
    deletaArquivosAuxiliares()

    #tratamentoArquivoFinal()

#Função para criar o gráfico principal

def formataData(data):
    #2022-07-15 00:00:00
    dataFormatoAntigo = str(data).split(' ')[0]
    vetorData = dataFormatoAntigo.split('-')
    return vetorData[2] + '/' + vetorData[1] + '/' + vetorData[0]

def formataNrcEmotions(emotion):

    dicionario_retorno = {}

    if emotion != 'None':
        if '*' in emotion:
            todas_emocoes = emotion.split('*')
            for unica_emocao in todas_emocoes:
                nome_emocao = unica_emocao.split(':')[0]
                valor_emocao = unica_emocao.split(':')[1]
                dicionario_retorno[nome_emocao] = valor_emocao
        else:
            nome_emocao = emotion.split(':')[0]
            valor_emocao = emotion.split(':')[1]
            dicionario_retorno[nome_emocao] = valor_emocao

    return dicionario_retorno

def formataGoogleEmotions(emotion):

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

def criaGraficoMetricas():

    #Prepara os dados

    df = pd.read_csv('./dados_metricas.csv', sep=';', index_col=False)

    df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
    df = df.sort_values(by=['data'])
    df['data'] = df['data'].map(formataData)
    df = df.reset_index()
    df = df.drop(labels='index', axis=1)
    df['polaridade'] = pd.to_numeric(df['polaridade'])

    retorno_nrc_emocoes = df['NRC_EMOTIONS'].map(formataNrcEmotions)
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
        array_nome_nrc_emocoes.append('trust')

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
                
    for chave in dict_nrc_emocoes.keys():
        while len(dict_nrc_emocoes[chave]) < 10:
            dict_nrc_emocoes[chave].append(np.nan)
        
    #NRC - Tratamento valores de cada emoção (1 coluna pra cada)
    for emocao_nrc in array_nome_nrc_emocoes:
        df[emocao_nrc] = dict_nrc_emocoes[emocao_nrc]   

    #NRC - Adiciona uma coluna contendo todos os nomes das emoções
    data = {'NOMES_NRC_EMOCOES': array_nome_nrc_emocoes}
    df['NOMES_NRC_EMOCOES'] = data['NOMES_NRC_EMOCOES']

    #NRC - Cria colunas para saber qual linha tem determinada emoção
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


    #df = df.drop(labels='mensagem', axis=1) #Teste
    df = df.drop(labels='NRC_EMOTIONS', axis=1) #Teste
    #df = df.drop(labels='GooglePerspectiveMetrics', axis=1) #Teste

    retorno_google_emocoes = df['GooglePerspectiveMetrics'].map(formataGoogleEmotions)

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
    data = {'NOMES_GOOGLE_EMOCOES': array_nome_google_emocoes}
    df['NOMES_GOOGLE_EMOCOES'] = data['NOMES_GOOGLE_EMOCOES']

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
   
    
    print(df[:])
    #tratamentoArquivoFinal()



    #

    app = dash.Dash(__name__)

    app.layout = html.Div([

        #Primeiro gráfico

         html.Div([
            dcc.Graph(
            figure={
                'data': [
                    {'x': df['data'], 'y': df['polaridade'], 'type': 'bar', 'name': 'SF'},
                    #{'x': df['data'], 'y': df['polaridade'], 'type': 'bar', 'name': u'Montréal'},
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
                value=df['idUsuario'][0],
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
                value=df['idUsuario'][0],
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
                value=df_combos['EMOCOES_COMBO'][0],
                multi=False,
                disabled=False,
                clearable=True,
                searchable=True,
                placeholder='Escolha uma Métrica...',
                className='form-dropdown',
                style={'width':"90%"},
                persistence='string',
                persistence_type='memory'),
     
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
        Output('grafico_metricas','figure'),
        [Input('cboAlunos','value'),
        Input('cboNrcEmotion','value')]
    )

    def atualiza_grafico_metricas_nrc(alunos, nrc_emotion):
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
        dff=df[ dff_aux_alunos & (df['TEM_' + nrc_emotion.upper()]==nrc_emotion)]

        #Teste Data em modo DateTime
        #dff['data'] = pd.to_datetime(dff['data'], format='%d/%m/%Y')
        #dff = dff.sort_values(by=['data'])
        #Teste

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
        return fig

    webbrowser.open('http://127.0.0.1:8050')
    app.run_server(debug=False)

if __name__ == '__main__':

    # Pega informações do usuário

    listaCursosUsuario, idUsuarioBuscado = pegaInformacoesUsuario()

    # Seleciona o curso

    idDisciplinaEscolhida = menuSelecaoCurso(listaCursosUsuario)

    # Pega as mensagens dos chats do curso

    cursosArray = coletaMensagensChatDoCurso(idDisciplinaEscolhida)

    # Pega as direct messages

    coletaMensagensDiretasAoProfessor(cursosArray, idUsuarioBuscado)

    # Pega as mensagens dos fóruns

    coletaMensagensDosForuns(cursosArray)

    #A partir daqui, fazer um único CSV que tenha idUsuario;Mensagem;data
    #Deletar CSVs antigos e deixar somente o novo

    leituraArquivos = LeituraCsvs()

    retornoMensagensChats = leituraArquivos.get_dados_chats_mensagens()
    vetorMensagensChat = retornoMensagensChats.loc[:, 'message'].values

    retornoMensagensDiretas = leituraArquivos.get_dados_mensagens_diretas()
    vetorMensagensDiretas = retornoMensagensDiretas.loc[:, 'fullmessage'].values

    retornoMensagensPostsForuns = leituraArquivos.get_dados_posts()
    vetorMensagensPostsForuns = retornoMensagensPostsForuns.loc[:, 'message'].values

    #Preparação Dados para análise
    gravaCsvUnico(retornoMensagensChats.loc[:].values, retornoMensagensDiretas.loc[:].values, retornoMensagensPostsForuns.loc[:].values)

    retornoMensagens = pd.read_csv('./dados_mensagens.csv', sep=';')

    analiseMetricas(retornoMensagens.loc[:].values)
    
    criaGraficoMetricas()

