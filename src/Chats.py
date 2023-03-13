from src.MoodleApi import *
from datetime import datetime

class Chats():

    def __init__(self, courseArrays, moodle_api):

        self.chat_messages = {}
        self.moodle_api = moodle_api

        chats_data = self.moodle_api.call('mod_chat_get_chats_by_courses', courseids=courseArrays)
        self.grava_csv_dados_chats(chats_data)
        self.chats = {}
        for chat in chats_data['chats']:
            self.chats[chat['id']] = chat['name']

    def get_messages_from_chat_id(self, chatId):
        dados_sessoes = self.moodle_api.call('mod_chat_get_sessions', chatid=chatId, showall=1)

        for sessao in dados_sessoes['sessions']:
            if len(sessao['sessionusers']) > 0:
                mensagens_sessoes = self.moodle_api.call('mod_chat_get_session_messages', chatid=chatId, sessionstart=sessao['sessionstart'], sessionend=sessao['sessionend'])
                for mensagem in mensagens_sessoes['messages']:
                    conteudoMensagem = mensagem['message'].replace('\xa0', '').replace('\n', '').replace('-', '').replace('*', '')
                    if conteudoMensagem != 'enter' and conteudoMensagem != 'exit':
                        dataMensagemChatObject = datetime.fromtimestamp(mensagem['timestamp'])
                        dataFormatada = str(dataMensagemChatObject.day).zfill(2) + '/' + str(dataMensagemChatObject.month).zfill(2) + '/' + str(dataMensagemChatObject.year)

                        self.chat_messages[mensagem['id']] = conteudoMensagem + '*' + str(mensagem['chatid']) + \
                            '*' + str(mensagem['userid']) + \
                            '*' + dataFormatada

        self.reescreve_csv_dados_chat_com_mensagens()

    def grava_csv_dados_chats(self, dados_chats):
        with open('./data/dados_chats.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = write_csv(csvfile, delimiter='-')
            writer.writerow(['idchat', 'course', 'namechat', 'section'])

            for chat in dados_chats['chats']:
                writer.writerow([chat['id'], chat['course'],
                                chat['name'], chat['section']])

    def reescreve_csv_dados_chat_com_mensagens(self):
        with open('./data/dados_chats.csv', 'r', newline='', encoding='utf-8') as csvfile:
            reader = read_csv(csvfile, delimiter='-')
            with open('./data/dados_chats_mensagens.csv', 'w', newline='', encoding='utf-8') as csvfilewrite:
                writer = write_csv(csvfilewrite, delimiter='-')

                for i, linha in enumerate(reader):
                    if i == 0:
                        # cabeçalho
                        writer.writerow(
                            [linha[0], linha[1], linha[2], linha[3], 'idmensagem', 'userid', 'message', 'data'])
                    else:
                        # valores
                        for mensagem in self.chat_messages:
                            idMensagem = mensagem
                            dados_mensagem = self.chat_messages[idMensagem]
                            dados_mensagem = dados_mensagem.split('*')
                            conteudoMensagem = dados_mensagem[0]
                            mensagemChatId = dados_mensagem[1]
                            userId = dados_mensagem[2]
                            data = dados_mensagem[3]
                            if conteudoMensagem != 'enter' and conteudoMensagem != 'exit':
                                if int(mensagemChatId) == int(linha[0]):
                                    writer.writerow([linha[0], linha[1], linha[2], linha[3], idMensagem, userId, conteudoMensagem, data])