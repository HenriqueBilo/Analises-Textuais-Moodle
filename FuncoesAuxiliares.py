from Autenticacao import *
from Cursos import *
from Chats import *
from Usuarios import *
from Foruns import *
from Discussoes import *
from Postagens import *

import os

class FuncoesAuxiliares():
    def pega_informacoes_usuario(self):
        usuario = input('Informe seu usuário (matrícula): ')

        #emailArray = []
        #emailArray.append(usuario)
        realizaLogin = Autenticacao(usuario.zfill(8))
        idUsuarioBuscado = realizaLogin.login()

        listaCursosUsuario = Cursos()
        listaCursosUsuario.busca_curso_por_usuario(idUsuarioBuscado)
        return listaCursosUsuario, idUsuarioBuscado

    def menu_selecao_curso(self, listaCursosUsuario):
        print('Selecione a disciplina desejada: \n')
        contadorDisciplina = 0
        dicionarioDisciplinas = {}
        for curso in listaCursosUsuario.courses:
            contadorDisciplina = contadorDisciplina + 1
            dicionarioDisciplinas[contadorDisciplina] = listaCursosUsuario.courses[curso] + \
                ' * ' + str(curso)
            print(str(contadorDisciplina) + ' - ' + listaCursosUsuario.courses[curso])

        disciplinaEscolhida = input()
        nomeDisciplinaEscolhida = dicionarioDisciplinas[int(disciplinaEscolhida)]
        idDisciplinaEscolhida = int(nomeDisciplinaEscolhida.split('*')[1])
        return idDisciplinaEscolhida

    def coleta_mensagens_chat_do_curso(self, idDisciplinaEscolhida):
        cursosArray = []
        cursosArray.append(idDisciplinaEscolhida)

        retorno = Chats(cursosArray)
        for chat in retorno.chats:
            retorno.get_messages_from_chat_id(chat)
        os.remove('./data/dados_chats.csv')

        return cursosArray

    def coleta_mensagens_diretas_ao_professor(self, cursosArray, idUsuarioBuscado):
        usersArray = []
        for curso in cursosArray:
            retorno = Usuarios(curso, idUsuarioBuscado)
            usersArray.append(retorno.users)

        directMessagesArray = {}
        for user in usersArray:
            for userId in user:
                if userId == idUsuarioBuscado:
                    retorno = call('core_message_get_messages', useridto=userId, useridfrom=0, type='conversations', read=1)

                    for msg in retorno['messages']:
                        if msg['useridfrom'] in user and msg['useridto'] in user:
                            dataMensagemChatObject = datetime.fromtimestamp(msg['timecreated'])
                            dataFormatada = str(dataMensagemChatObject.day).zfill(2) + '/' + str(dataMensagemChatObject.month).zfill(2) + '/' + str(dataMensagemChatObject.year)
                            
                            msg['fullmessage'] = msg['fullmessage'].replace('\xa0', '').replace('\n', ' ').replace('-', '').replace('*', '')
                            
                            directMessagesArray[msg['id']] = str(msg['useridfrom']) + '*' + str(msg['useridto']) + '*' \
                                + msg['fullmessage'].split('Este email é a cópia de uma mensagem que foi enviada para você em')[0] + '*' + dataFormatada

        with open('./data/dados_mensagens_diretas.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter='-')
            writer.writerow(['idmensagemdireta', 'useridfrom', 'useridto', 'fullmessage', 'data'])

            for mensagem_direta in directMessagesArray:
                idMensagemDireta = mensagem_direta
                dadosMensagem = directMessagesArray[idMensagemDireta].split('*')
                writer.writerow([idMensagemDireta, dadosMensagem[0], dadosMensagem[1], dadosMensagem[2], dadosMensagem[3]])

    def coleta_mensagens_dos_foruns(self, cursosArray):
        listaDeForums = Foruns(cursosArray)

        discussionsArray = []
        for forum in listaDeForums.forums:
            retorno = Discussoes(forum)
            discussionsArray.append(retorno.discussions)

        postagens = Postagens()
        for discussion in discussionsArray:
            for discussionId in discussion:
                postagens.coleta_postagens(discussionId)
        postagens.grava_csv_posts()

    def adiciona_nova_coluna(self, input_file, output_file, coluna_nova, array_valores_novos):
        with open(input_file, 'r', encoding='utf-8') as read_obj, \
            open(output_file, 'w', newline='', encoding='utf-8') as write_obj:
            csv_reader = csv.reader(read_obj, delimiter='-')
            csv_writer = csv.writer(write_obj, delimiter='-')
            for i, linha in enumerate(csv_reader):
                if i == 0:
                    linha.append(coluna_nova)
                else:
                    linha.append(array_valores_novos[i-1])

                csv_writer.writerow(linha)

    def grava_csv_unico(self, retornoMensagensChats, retornoMensagensDiretas, retornoMensagensPostsForuns):
        with open('./data/dados_mensagens.csv', 'w', newline='', encoding='utf-8') as csvfilewrite:
            writer = csv.writer(csvfilewrite, delimiter='-')
            writer.writerow(['idUsuario', 'mensagem', 'data'])

            for msgChat in retornoMensagensChats:
                writer.writerow([msgChat[5], msgChat[6],msgChat[7]])

            for msgDireta in retornoMensagensDiretas:
                writer.writerow([msgDireta[1], msgDireta[3],msgDireta[4]])

            for msgPost in retornoMensagensPostsForuns:
                writer.writerow([msgPost[3], msgPost[2],msgPost[4]])

    def deleta_arquivos_auxiliares(self):
        #Deleta arquivos auxiliares
        array_arquivos_deletar = ['./data/dados_chats_mensagens.csv', './data/dados_cursos.csv', './data/dados_discussions.csv', './data/dados_foruns.csv', 
                                './data/dados_mensagens_diretas.csv', './data/dados_posts.csv', './data/dados_usuario.csv', './data/dados_mensagens_aux_polaridade_e_nrc_emotions.csv',
                                './data/dados_mensagens_aux_polaridade.csv', './data/dados_mensagens.csv']

        for arquivo in array_arquivos_deletar:
            if os.path.isfile(arquivo):
                os.remove(arquivo)