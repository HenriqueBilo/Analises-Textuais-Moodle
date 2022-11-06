from MoodleApi import *

class Autenticacao():

    def __init__(self, username):
        self.username = username

    def login(self):
        infos_usuario = call('core_user_get_users_by_field', field='username', values=[self.username])
        return infos_usuario[0]['id']