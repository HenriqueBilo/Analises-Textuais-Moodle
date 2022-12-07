import pandas as pd
import os

class LeituraCsvs():
    def __init__(self):
        if os.path.exists('./data/dados_usuario.csv'):
            self.dados_usuario = pd.read_csv('./data/dados_usuario.csv', sep='-')
        else:
            self.dados_usuario = pd.DataFrame()

        if os.path.exists('./data/dados_posts.csv'):
            self.dados_posts = pd.read_csv('./data/dados_posts.csv', sep='-')
        else:
            self.dados_posts = pd.DataFrame()

        if os.path.exists('./data/dados_mensagens_diretas.csv'):
            self.dados_mensagens_diretas = pd.read_csv('./data/dados_mensagens_diretas.csv', sep='-')
        else:
            self.dados_mensagens_diretas = pd.DataFrame()

        if os.path.exists('./data/dados_foruns.csv'):
            self.dados_foruns = pd.read_csv('./data/dados_foruns.csv', sep='-')
        else:
            self.dados_foruns = pd.DataFrame()

        if os.path.exists('./data/dados_discussions.csv'):
            self.dados_discussions = pd.read_csv('./data/dados_discussions.csv', sep='-')
        else:
            self.dados_discussions = pd.DataFrame()

        if os.path.exists('./data/dados_cursos.csv'):
            self.dados_cursos = pd.read_csv('./data/dados_cursos.csv', sep='-')
        else:
            self.dados_cursos = pd.DataFrame()

        if os.path.exists('./data/dados_chats_mensagens.csv'):
            self.dados_chats_mensagens = pd.read_csv('./data/dados_chats_mensagens.csv', sep='-')
        else:
            self.dados_chats_mensagens = pd.DataFrame()

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