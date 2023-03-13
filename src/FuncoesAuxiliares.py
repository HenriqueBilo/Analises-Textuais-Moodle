from src.Autenticacao import *
from src.Cursos import *
from src.Chats import *
from src.Usuarios import *
from src.Foruns import *
from src.Discussoes import *
from src.Postagens import *
from src.MoodleApi import *

from os import environ, remove as os_remove, path as os_path
from pwinput import pwinput as pw_input

class FuncoesAuxiliares():

    def __init__(self):
        self.moodle_api = MoodleApi()

    def pega_informacoes_usuario(self):
        while True:
            usuario = input('Informe seu usuário (matrícula UFRGS): ')
            senha = pw_input('Informe sua senha: ')

            usuario = usuario.zfill(8)

            retorno_token = self.moodle_api.criar_token(usuario, senha)
            if retorno_token:
                break
            
            print('\nUsuário ou senha inválidos. Tente novamente')
        
        realizaLogin = Autenticacao(usuario, self.moodle_api)
        idUsuarioBuscado = realizaLogin.login()

        listaCursosUsuario = Cursos(self.moodle_api)
        listaCursosUsuario.busca_curso_por_usuario(idUsuarioBuscado)
        return listaCursosUsuario, idUsuarioBuscado

    def menu_selecao_curso(self, listaCursosUsuario):
        while True:
            contadorDisciplina = 0
            dicionarioDisciplinas = {}

            print('0 - Sair')
            for curso in listaCursosUsuario.courses:
                contadorDisciplina = contadorDisciplina + 1
                dicionarioDisciplinas[str(contadorDisciplina)] = listaCursosUsuario.courses[curso] + \
                    ' * ' + str(curso)
                print(str(contadorDisciplina) + ' - ' + listaCursosUsuario.courses[curso])

            disciplinaEscolhida = input('\nDigite o número da disciplina desejada para realizar a análise: ')
            if disciplinaEscolhida == '0':
                return '0'
            if disciplinaEscolhida not in dicionarioDisciplinas and disciplinaEscolhida != '0':
                print('\nDisciplina escolhida inválida. Tente novamente')
            else:
                break

        nomeDisciplinaEscolhida = dicionarioDisciplinas[disciplinaEscolhida]
        idDisciplinaEscolhida = int(nomeDisciplinaEscolhida.split('*')[1])
        
        return idDisciplinaEscolhida

    def coleta_mensagens_chat_do_curso(self, idDisciplinaEscolhida):
        cursosArray = []
        cursosArray.append(idDisciplinaEscolhida)

        retorno = Chats(cursosArray, self.moodle_api)
        for chat in retorno.chats:
            retorno.get_messages_from_chat_id(chat)

        os_remove('./data/dados_chats.csv')

        return cursosArray

    def coleta_mensagens_diretas_ao_professor(self, cursosArray, idUsuarioBuscado):
        usersArray = []
        for curso in cursosArray:
            retorno = Usuarios(curso, idUsuarioBuscado, self.moodle_api)
            usersArray.append(retorno.users)
            
        directMessagesArray = {}
        for user in usersArray:
            for userId in user:
                if userId == idUsuarioBuscado and (user[userId].split('*')[1] != 'Aluno' and user[userId].split('*')[1] != 'Visitante'):
                    retorno = self.moodle_api.call('core_message_get_messages', useridto=userId, useridfrom=0, type='conversations', read=1)

                    for msg in retorno['messages']:
                        if msg['useridfrom'] in user and msg['useridto'] in user:
                            dataMensagemChatObject = datetime.fromtimestamp(msg['timecreated'])
                            dataFormatada = str(dataMensagemChatObject.day).zfill(2) + '/' + str(dataMensagemChatObject.month).zfill(2) + '/' + str(dataMensagemChatObject.year)
                            
                            msg['fullmessage'] = msg['fullmessage'].replace('\xa0', '').replace('\n', ' ').replace('-', '').replace('*', '')
                            
                            directMessagesArray[msg['id']] = str(msg['useridfrom']) + '*' + str(msg['useridto']) + '*' \
                                + msg['fullmessage'].split('Este email é a cópia de uma mensagem que foi enviada para você em')[0] + '*' + dataFormatada

        with open('./data/dados_mensagens_diretas.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = write_csv(csvfile, delimiter='-')
            writer.writerow(['idmensagemdireta', 'useridfrom', 'useridto', 'fullmessage', 'data'])

            for mensagem_direta in directMessagesArray:
                idMensagemDireta = mensagem_direta
                dadosMensagem = directMessagesArray[idMensagemDireta].split('*')
                writer.writerow([idMensagemDireta, dadosMensagem[0], dadosMensagem[1], dadosMensagem[2], dadosMensagem[3]])

    def coleta_mensagens_dos_foruns(self, cursosArray, dadosUsuarios):
        listaDeForums = Foruns(cursosArray, self.moodle_api)

        discussionsArray = []
        for forum in listaDeForums.forums:
            retorno = Discussoes(forum, self.moodle_api)
            discussionsArray.append(retorno.discussions)

        postagens = Postagens(self.moodle_api, dadosUsuarios)
        for discussion in discussionsArray:
            for discussionId in discussion:
                postagens.coleta_postagens(discussionId)

        postagens.grava_csv_posts()

    def adiciona_nova_coluna(self, input_file, output_file, coluna_nova, array_valores_novos):
        with open(input_file, 'r', encoding='utf-8') as read_obj, \
            open(output_file, 'w', newline='', encoding='utf-8') as write_obj:
            csv_reader = read_csv(read_obj, delimiter='-')
            csv_writer = write_csv(write_obj, delimiter='-')
            for i, linha in enumerate(csv_reader):
                if i == 0:
                    linha.append(coluna_nova)
                else:
                    linha.append(array_valores_novos[i-1])

                csv_writer.writerow(linha)

    def adiciona_nova_coluna_dict(self, input_file, output_file, coluna_nova, dict_valores_novos):
        with open(input_file, 'r', encoding='utf-8') as read_obj, \
            open(output_file, 'w', newline='', encoding='utf-8') as write_obj:
            csv_reader = read_csv(read_obj, delimiter='-')
            csv_writer = write_csv(write_obj, delimiter='-')
            for i, linha in enumerate(csv_reader):
                if i == 0:
                    linha.append(coluna_nova)
                else:
                    linha.append(dict_valores_novos[i])

                csv_writer.writerow(linha)

    def grava_csv_unico(self, retornoMensagensChats, retornoMensagensDiretas, retornoMensagensPostsForuns):
        with open('./data/dados_mensagens.csv', 'w', newline='', encoding='utf-8') as csvfilewrite:
            writer = write_csv(csvfilewrite, delimiter='-')
            writer.writerow(['idUsuario', 'mensagem', 'data'])

            for msgChat in retornoMensagensChats:
                writer.writerow([msgChat[5], msgChat[6],msgChat[7]])

            for msgDireta in retornoMensagensDiretas:
                writer.writerow([msgDireta[1], msgDireta[3],msgDireta[4]])

            for msgPost in retornoMensagensPostsForuns:
                writer.writerow([msgPost[3], msgPost[2],msgPost[4]])

    def deleta_arquivos_auxiliares(self):
        array_arquivos_deletar = ['./data/dados_chats_mensagens.csv', './data/dados_cursos.csv', './data/dados_discussions.csv', './data/dados_foruns.csv', 
                                './data/dados_mensagens_diretas.csv', './data/dados_posts.csv', './data/dados_usuario.csv', './data/dados_mensagens_aux_polaridade_e_nrc_emotions.csv',
                                './data/dados_mensagens_aux_polaridade.csv', './data/dados_mensagens.csv', './data/dados_metricas_finais.csv', './data/dados_metricas.csv']

        for arquivo in array_arquivos_deletar:
            if os_path.isfile(arquivo):
                os_remove(arquivo)

    def barra_progresso(self, progresso, total, prefixo, sufixo = ''):
        percentual = 100 * (progresso / float(total))
        barra = '█' * int(percentual) + '-' * (100 - int(percentual))
        print(f'\r{prefixo} |{barra}| {int(percentual)}%', end='\r', flush = True)