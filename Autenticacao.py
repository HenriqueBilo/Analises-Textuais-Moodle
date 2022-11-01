from MoodleApi import *

class Autenticacao():

    def __init__(self, email):
        self.emailArray = email

    def login(self):
        infos_usuario = call('core_user_get_users_by_field', field='email', values=self.emailArray)
        return infos_usuario[0]['id']