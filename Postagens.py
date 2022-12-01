from MoodleApi import *
import csv
from bs4 import BeautifulSoup
from datetime import datetime

class Postagens():
    '''Retorna a lista de posts de uma determinada discussão'''

    def __init__(self, moodle_api):
        self.moodle_api = moodle_api
        self.posts = {}

    def coleta_postagens(self, discussionId):
        posts_data = self.moodle_api.call('mod_forum_get_discussion_posts', discussionid=discussionId)
        for post in posts_data['posts']:
            dataMensagemChatObject = datetime.fromtimestamp(post['timecreated'])
            dataFormatada = str(dataMensagemChatObject.day).zfill(2) + '/' + str(dataMensagemChatObject.month).zfill(2) + '/' + str(dataMensagemChatObject.year)

            soup = BeautifulSoup(post['message'], 'html.parser')
            self.posts[post['id']] = post['subject'] + '*' + \
                soup.get_text().replace('\xa0', '').replace('\n', ' ').replace('-', '').replace('*', '') + '*' + str(post['author']['id']) + '*' + dataFormatada

    def grava_csv_posts(self):
        with open('./data/dados_posts.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter='-')
            writer.writerow(['id', 'subject', 'message', 'autor', 'data'])

            for post in self.posts:
                idPost = post
                dados_posts = self.posts[post]
                dados_posts = dados_posts.split('*')

                writer.writerow(
                    [idPost, dados_posts[0], dados_posts[1], dados_posts[2], dados_posts[3]])