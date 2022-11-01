import pandas as pd

class LeituraCsvs():
    def __init__(self):
        self.dados_usuario = pd.read_csv('./dados_usuario.csv', sep=';')
        self.dados_posts = pd.read_csv('./dados_posts.csv', sep=';')
        self.dados_mensagens_diretas = pd.read_csv('./dados_mensagens_diretas.csv', sep=';')
        self.dados_foruns = pd.read_csv('./dados_foruns.csv', sep=';')
        self.dados_discussions = pd.read_csv('./dados_discussions.csv', sep=';')
        self.dados_cursos = pd.read_csv('./dados_cursos.csv', sep=';')
        self.dados_chats_mensagens = pd.read_csv('./dados_chats_mensagens.csv', sep=';')

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