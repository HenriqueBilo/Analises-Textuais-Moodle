from Autenticacao import *
from Cursos import *
from Chats import *
from Usuarios import *
from Foruns import *
from Discussoes import *
from Postagens import *

import os

class FuncoesDeColeta():
    def pega_informacoes_usuario(self):
        usuario = input('Informe seu usuário: ')

        emailArray = []
        emailArray.append(usuario)
        realizaLogin = Autenticacao(emailArray)
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
        os.remove('./dados_chats.csv')

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
                    retorno = call('core_message_get_messages', useridto=userId, useridfrom=0, type='conversations', read=2)

                    for msg in retorno['messages']:
                        if msg['useridfrom'] in user and msg['useridto'] in user:
                            dataMensagemChatObject = datetime.fromtimestamp(msg['timecreated'])
                            dataFormatada = str(dataMensagemChatObject.day).zfill(2) + '/' + str(dataMensagemChatObject.month).zfill(2) + '/' + str(dataMensagemChatObject.year)
                            directMessagesArray[msg['id']] = str(msg['useridfrom']) + '*' + str(msg['useridto']) + '*' + msg['fullmessage'] + '*' + dataFormatada

        with open('./dados_mensagens_diretas.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='|')
            writer.writerow(['idmensagemdireta', 'useridfrom', 'useridto', 'fullmessage', 'data'])

            for mensagem_direta in directMessagesArray:
                idMensagemDireta = mensagem_direta
                dadosMensagem = directMessagesArray[idMensagemDireta].split('*')
                writer.writerow([idMensagemDireta, dadosMensagem[0], dadosMensagem[1], dadosMensagem[2], dadosMensagem[3]])

    def coleta_mensagens_dos_foruns(self, cursosArray):
        listaDeForums = Foruns(cursosArray)

        discussionsArray = []
        for forum in listaDeForums.forums:
            forum = listaDeForums.forums[forum].split('*')
            retorno = Discussoes(forum[0])
            discussionsArray.append(retorno.discussions)

        postsArray = []
        for discussion in discussionsArray:
            for discussionId in discussion:
                retorno = Postagens(discussionId)
                postsArray.append(retorno.posts)
