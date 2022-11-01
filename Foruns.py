from MoodleApi import *
import csv

class Foruns():
    '''Retorna uma lista de foruns'''

    def __init__(self, arrayForums):
        forums_data = call('mod_forum_get_forums_by_courses', courseids=arrayForums)
        self.forums = {}
        for forum in forums_data:
            self.forums[forum['id']] = str(forum['course']) + '*' + forum['name'] + '*' + forum['intro']
        self.grava_csv_forums()

    def grava_csv_forums(self):
        with open('./dados_foruns.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='|')
            writer.writerow(['id', 'course', 'name', 'intro'])

            for forum in self.forums:
                idForum = forum
                dados_foruns = self.forums[forum]
                dados_foruns = dados_foruns.split('*')

                writer.writerow([idForum, dados_foruns[0], dados_foruns[1], dados_foruns[2]])