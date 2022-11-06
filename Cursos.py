from MoodleApi import *
import csv

class Cursos():
    '''Classe que pega todos os cursos que um determinado usuário participa'''

    def __init__(self):
        self.courses = {}

    def busca_curso_por_usuario(self, idUsuario):
        dados_cursos = call('core_enrol_get_users_courses', userid=idUsuario)
        self.grava_csv_dados_cursos(dados_cursos)
        for dados in dados_cursos:
            # VERIFICAR depois se isso funciona 100%
            if dados['progress'] == None:
                self.courses[dados['id']] = dados['displayname']

    def grava_csv_dados_cursos(self, dados_cursos):
        with open('./data/dados_cursos.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter='-')
            writer.writerow(['id', 'nome', 'categoria'])

            for curso in dados_cursos:
                if curso['progress'] == None:
                    writer.writerow(
                        [curso['id'], curso['fullname'], curso['category']])