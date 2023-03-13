from src.MoodleApi import *

class Autenticacao():

    def __init__(self, username, moodle_api):
        self.username = username
        self.moodle_api = moodle_api

    def login(self):
        infos_usuario = self.moodle_api.call('core_user_get_users_by_field', field='username', values=[self.username])
        return infos_usuario[0]['id']