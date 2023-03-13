from src.MoodleApi import *

class Foruns():
    '''Retorna uma lista de foruns'''

    def __init__(self, arrayForums, moodle_api):
        self.moodle_api = moodle_api

        forums_data = self.moodle_api.call('mod_forum_get_forums_by_courses', courseids=arrayForums)
        self.forums = {}
        for forum in forums_data:
            self.forums[forum['id']] = str(forum['course']) + '*' + forum['name']
        self.grava_csv_forums()

    def grava_csv_forums(self):
        with open('./data/dados_foruns.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = write_csv(csvfile, delimiter='-')
            writer.writerow(['id', 'course', 'name'])

            for forum in self.forums:
                idForum = forum
                dados_foruns = self.forums[forum]
                dados_foruns = dados_foruns.split('*')

                writer.writerow([idForum, dados_foruns[0], dados_foruns[1]])