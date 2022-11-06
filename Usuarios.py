from MoodleApi import *
import csv

class Usuarios():
    def __init__(self, course, idUsuarioBuscado):
        "Pega os usuários de um curso específico"
        users_data = call('core_enrol_get_enrolled_users', courseid=course)
        self.idUsuarioBuscado = idUsuarioBuscado
        self.users = {}
        for data in users_data:
            self.users[data['id']] = data['fullname']
        self.grava_csv_usuario(users_data)

    def grava_csv_usuario(self, infos_usuario):
        with open('./data/dados_usuario.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter='-')
            writer.writerow(['id', 'nome', 'email', 'professor'])

            for usuario in infos_usuario:
                # if usuario['id'] == self.idUsuarioBuscado:
                # Verificar com o Wives essa validação
                if len(usuario['roles']) > 0:
                    cargoNoCurso = usuario['roles'][0]['shortname']
                else:
                    cargoNoCurso = 'None'
                if cargoNoCurso == 'editingteacher' or cargoNoCurso == 'teacher' or cargoNoCurso == 'professor' \
                    or cargoNoCurso == 'tutor_a' or cargoNoCurso == 'profcoord':
                    if usuario.get('email') != None:
                        writer.writerow([usuario['id'], usuario['fullname'], usuario['email'].replace('|', ''), 'Sim'])
                    else:
                        writer.writerow([usuario['id'], usuario['fullname'], 'None', 'Sim'])
                else:
                    if usuario.get('email') != None:
                        writer.writerow([usuario['id'], usuario['fullname'], usuario['email'].replace('|', ''), 'Nao'])
                    else:
                        writer.writerow([usuario['id'], usuario['fullname'], 'None', 'Nao'])