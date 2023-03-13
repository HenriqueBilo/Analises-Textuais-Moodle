from src.MoodleApi import *

class Usuarios():
    def __init__(self, course, idUsuarioBuscado, moodle_api):
        self.moodle_api = moodle_api

        "Pega os usuários de um curso específico"
        users_data = self.moodle_api.call('core_enrol_get_enrolled_users', courseid=course)
        self.idUsuarioBuscado = idUsuarioBuscado
        self.users = {}
        for data in users_data:
            if len(data['roles']) > 0:
                self.users[data['id']] = data['fullname'] + '*' + data['roles'][0]['name']
            else:
                self.users[data['id']] = data['fullname'] + '*' + 'Aluno'
        self.grava_csv_usuario(users_data)

    def grava_csv_usuario(self, infos_usuario):
        with open('./data/dados_usuarios.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = write_csv(csvfile, delimiter='-')
            writer.writerow(['id', 'nome', 'email', 'professor'])

            for usuario in infos_usuario:
                if len(usuario['roles']) > 0:
                    cargoNoCurso = usuario['roles'][0]['name']
                else:
                    cargoNoCurso = 'None'
                if cargoNoCurso != 'Aluno' and cargoNoCurso != 'Visitante':
                    if usuario.get('email') != None:
                        writer.writerow([usuario['id'], usuario['fullname'], usuario['email'].replace('|', ''), 'Sim'])
                    else:
                        writer.writerow([usuario['id'], usuario['fullname'], 'None', 'Sim'])
                else:
                    if usuario.get('email') != None:
                        writer.writerow([usuario['id'], usuario['fullname'], usuario['email'].replace('|', ''), 'Nao'])
                    else:
                        writer.writerow([usuario['id'], usuario['fullname'], 'None', 'Nao'])