from src.MoodleApi import *
from bs4 import BeautifulSoup

class Discussoes():
    '''Retorna uma lista de discussões de um determinado fórum'''

    def __init__(self, forumId, moodle_api):
        self.moodle_api = moodle_api

        discussions_data = self.moodle_api.call('mod_forum_get_forum_discussions', forumid=forumId)
        self.discussions = {}
        for discussion in discussions_data['discussions']:
            soup = BeautifulSoup(discussion['message'], 'html.parser')
            self.discussions[discussion['discussion']] = discussion['name'] + \
                '*' + discussion['subject'] + '*' + soup.get_text()
        self.grava_csv_discussions()

    def grava_csv_discussions(self):
        with open('./data/dados_discussions.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = write_csv(csvfile, delimiter='-')
            writer.writerow(['id', 'name', 'subject', 'message'])

            for discussion in self.discussions:
                idDiscussion = discussion
                dados_discussions = self.discussions[discussion]
                dados_discussions = dados_discussions.split('*')

                writer.writerow([idDiscussion, dados_discussions[0], dados_discussions[1], dados_discussions[2]])