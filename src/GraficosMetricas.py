from src.FuncoesAuxiliares import *

import pandas as pd
import numpy as np
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.express as px
import webbrowser
from datetime import date
import logging
import math as mt

class GraficosMetricas():
    def formata_data(self, data):
        data_formato_antigo = str(data).split(' ')[0]
        vetor_data = data_formato_antigo.split('-')
        return vetor_data[2] + '/' + vetor_data[1] + '/' + vetor_data[0]

    def formata_nrc_emotions(self, emotion):
        dicionario_retorno = {}

        if emotion != 'None':
            if '*' in emotion:
                todas_emocoes = emotion.split('*')
                for unica_emocao in todas_emocoes:
                    if unica_emocao != '':
                        nome_emocao = unica_emocao.split(':')[0]
                        valor_emocao = unica_emocao.split(':')[1]

                        nome_emocao = self.traduz_emocoes_nrc(nome_emocao)

                        dicionario_retorno[nome_emocao.upper()] = valor_emocao
            else:
                nome_emocao = emotion.split(':')[0]
                valor_emocao = emotion.split(':')[1]

                nome_emocao = self.traduz_emocoes_nrc(nome_emocao)

                dicionario_retorno[nome_emocao.upper()] = valor_emocao

        return dicionario_retorno

    def traduz_emocoes_nrc(self, emocao):
        if emocao == 'fear':
            return 'Medo'
        elif emocao == 'anger':
            return 'Raiva'
        elif emocao == 'anticipation':
            return 'Ansiedade'
        elif emocao == 'trust':
            return 'Confiança'
        elif emocao == 'surprise':
            return 'Surpresa'
        elif emocao == 'positive':
            return 'Positivo'
        elif emocao == 'negative':
            return 'Negativo'
        elif emocao == 'sadness':
            return 'Tristeza'
        elif emocao == 'disgust':
            return 'Desgosto'
        else:
            return 'Alegria'

    def formata_google_emotions(self, emotion):
        dicionario_retorno = {}

        if '*' in emotion:
            todas_emocoes = emotion.split('*')
            for unica_emocao in todas_emocoes:
                nome_emocao = unica_emocao.split(':')[0]

                if ' ' in nome_emocao.upper():
                    vet_emocao_formatada = nome_emocao.split(' ')
                    emocao_formatada = ''
                    for i, palavra in enumerate(vet_emocao_formatada):
                        if i == 0:
                            emocao_formatada += palavra
                        else:
                            emocao_formatada += '_' + palavra

                    valor_emocao = unica_emocao.split(':')[1]
                    dicionario_retorno[emocao_formatada] = float(valor_emocao)
                else:
                    valor_emocao = unica_emocao.split(':')[1]
                    dicionario_retorno[nome_emocao] = float(valor_emocao)
        else:
            nome_emocao = emotion.split(':')[0]

            if ' ' in nome_emocao.upper():
                vet_emocao_formatada = nome_emocao.split(' ')
                emocao_formatada = ''
                for i, palavra in enumerate(vet_emocao_formatada):
                    if i == 0 or i + 1 < len(vet_emocao_formatada):
                        emocao_formatada += palavra
                    else:
                        emocao_formatada += '_' + palavra
                valor_emocao = emotion.split(':')[1]
                dicionario_retorno[emocao_formatada] = float(valor_emocao)
            else:
                valor_emocao = emotion.split(':')[1]
                dicionario_retorno[nome_emocao] = float(valor_emocao)

        return dicionario_retorno

    def prepara_df_grafico_relatorio_geral_polaridade(self, aluno, df):
        df_aux = df[df['idUsuario'] == aluno]
        media_polaridade_aluno = df_aux['polaridade'].mean()

        array_polaridade = []
        array_polaridade.append(media_polaridade_aluno)
        return array_polaridade

    def prepara_df_grafico_relatorio_geral_nrc_emo(self, aluno, df):
        array_ansiedade, array_confiança = [], []
        
        df_aux = df[df['idUsuario'] == aluno]

        if hasattr(df_aux, 'ANSIEDADE'):
            media_ansiedade = df_aux['ANSIEDADE'].mean()
            if mt.isnan(media_ansiedade):
                array_ansiedade.append(0)
            else:    
                array_ansiedade.append(media_ansiedade)
        else:
            array_ansiedade.append(0)
        if hasattr(df_aux, 'CONFIANÇA'):
            media_confiança = df_aux['CONFIANÇA'].mean()
            if mt.isnan(media_confiança):
                array_confiança.append(0)
            else:
                array_confiança.append(media_confiança)
        else:
            array_confiança.append(0)

        return array_ansiedade, array_confiança

    def prepara_df_grafico_relatorio_geral_google_perspective(self, aluno, df):
        array_profanidade, array_toxicidade_severa, array_ataque_de_identidade = [], [], []
        array_ameaca, array_toxicidade, array_insulto = [], [], []

        df_aux = df[df['idUsuario'] == aluno]

        media_profanidade, media_toxicidade_severa = df_aux['PROFANIDADE'].mean(),  df_aux['TOXICIDADE_SEVERA'].mean()
        media_ataque_de_identidade, media_ameaca = df_aux['ATAQUE_DE_IDENTIDADE'].mean(), df_aux['AMEAÇA'].mean()
        media_toxicidade, media_insulto = df_aux['TOXICIDADE'].mean(), df_aux['INSULTO'].mean()

        array_profanidade.append(media_profanidade)
        array_toxicidade_severa.append(media_toxicidade_severa)
        array_ataque_de_identidade.append(media_ataque_de_identidade)
        array_ameaca.append(media_ameaca)
        array_toxicidade.append(media_toxicidade)
        array_insulto.append(media_insulto)
        
        return array_profanidade, array_toxicidade_severa, array_ataque_de_identidade, array_ameaca, array_toxicidade, array_insulto

    def prepara_df_grafico_relatorio_geral_emo_roberta(self, aluno, df):
        array_admiracao, array_diversao, array_raiva, array_aborrecimento, array_aprovacao = [], [], [], [], []
        array_cautela, array_confusao, array_curiosidade, array_desejo, array_desapontamento = [], [], [], [], []
        array_desaprovacao, array_desgosto, array_constrangimento, array_empolgacao, array_medo = [], [], [], [], []
        array_gratidao, array_sofrimento, array_alegria, array_amor, array_nervosismo = [], [], [], [], []
        array_otimismo, array_orgulho, array_realizacao, array_alivio, array_remorso = [], [], [], [], []
        array_tristeza, array_surpresa, array_neutro = [], [], []

        df_aux = df[df['idUsuario'] == aluno]

        if hasattr(df_aux, 'ADMIRAÇÃO') and not mt.isnan(df_aux['ADMIRAÇÃO'].mean()):
            media_admiracao = df_aux['ADMIRAÇÃO'].mean()
            array_admiracao.append(media_admiracao)
        else:
            array_admiracao.append(0)
        if hasattr(df_aux, 'DIVERSÃO') and not mt.isnan(df_aux['DIVERSÃO'].mean()):
            media_diversao = df_aux['DIVERSÃO'].mean()
            array_diversao.append(media_diversao)
        else:
            array_diversao.append(0)
        if hasattr(df_aux, 'RAIVA') and not mt.isnan(df_aux['RAIVA'].mean()):
            media_raiva = df_aux['RAIVA'].mean()
            array_raiva.append(media_raiva)
        else:
            array_raiva.append(0)
        if hasattr(df_aux, 'ABORRECIMENTO') and not mt.isnan(df_aux['ABORRECIMENTO'].mean()):
            media_aborrecimento = df_aux['ABORRECIMENTO'].mean()
            array_aborrecimento.append(media_aborrecimento)
        else:
            array_aborrecimento.append(0)
        if hasattr(df_aux, 'APROVAÇÃO') and not mt.isnan(df_aux['APROVAÇÃO'].mean()):
            media_aprovacao = df_aux['APROVAÇÃO'].mean()
            array_aprovacao.append(media_aprovacao)
        else:
            array_aprovacao.append(0)
        if hasattr(df_aux, 'CAUTELA') and not mt.isnan(df_aux['CAUTELA'].mean()):
            media_cautela = df_aux['CAUTELA'].mean()
            array_cautela.append(media_cautela)
        else:
            array_cautela.append(0)
        if hasattr(df_aux, 'CONFUSÃO') and not mt.isnan(df_aux['CONFUSÃO'].mean()):
            media_confusao = df_aux['CONFUSÃO'].mean()
            array_confusao.append(media_confusao)
        else:
            array_confusao.append(0)
        if hasattr(df_aux, 'CURIOSIDADE') and not mt.isnan(df_aux['CURIOSIDADE'].mean()):
            media_curiosidade = df_aux['CURIOSIDADE'].mean()
            array_curiosidade.append(media_curiosidade)
        else:
            array_curiosidade.append(0)
        if hasattr(df_aux, 'DESEJO') and not mt.isnan(df_aux['DESEJO'].mean()):
            media_desejo = df_aux['DESEJO'].mean()
            array_desejo.append(media_desejo)
        else:
            array_desejo.append(0)
        if hasattr(df_aux, 'DESAPONTAMENTO') and not mt.isnan(df_aux['DESAPONTAMENTO'].mean()):
            media_desapontamento = df_aux['DESAPONTAMENTO'].mean()
            array_desapontamento.append(media_desapontamento)
        else:
            array_desapontamento.append(0)
        if hasattr(df_aux, 'DESAPROVAÇÃO') and not mt.isnan(df_aux['DESAPROVAÇÃO'].mean()):
            media_desaprovacao = df_aux['DESAPROVAÇÃO'].mean()
            array_desaprovacao.append(media_desaprovacao)
        else:
            array_desaprovacao.append(0)
        if hasattr(df_aux, 'DESGOSTO') and not mt.isnan(df_aux['DESGOSTO'].mean()):
            media_desgosto = df_aux['DESGOSTO'].mean()
            array_desgosto.append(media_desgosto)
        else:
            array_desgosto.append(0)
        if hasattr(df_aux, 'CONSTRANGIMENTO') and not mt.isnan(df_aux['CONSTRANGIMENTO'].mean()):
            media_constrangimento = df_aux['CONSTRANGIMENTO'].mean()
            array_constrangimento.append(media_constrangimento)
        else:
            array_constrangimento.append(0)
        if hasattr(df_aux, 'EMPOLGAÇÃO') and not mt.isnan(df_aux['EMPOLGAÇÃO'].mean()):
            media_empolgacao = df_aux['EMPOLGAÇÃO'].mean()
            array_empolgacao.append(media_empolgacao)
        else:
            array_empolgacao.append(0)
        if hasattr(df_aux, 'MEDO') and not mt.isnan(df_aux['MEDO'].mean()):
            media_medo = df_aux['MEDO'].mean()
            array_medo.append(media_medo)
        else:
            array_medo.append(0)
        if hasattr(df_aux, 'GRATIDÃO') and not mt.isnan(df_aux['GRATIDÃO'].mean()):
            media_gratidao = df_aux['GRATIDÃO'].mean()
            array_gratidao.append(media_gratidao)
        else:
            array_gratidao.append(0)
        if hasattr(df_aux, 'SOFRIMENTO') and not mt.isnan(df_aux['SOFRIMENTO'].mean()):
            media_sofrimento = df_aux['SOFRIMENTO'].mean()
            array_sofrimento.append(media_sofrimento)
        else:
            array_sofrimento.append(0)
        if hasattr(df_aux, 'ALEGRIA') and not mt.isnan(df_aux['ALEGRIA'].mean()):
            media_alegria = df_aux['ALEGRIA'].mean()
            array_alegria.append(media_alegria)
        else:
            array_alegria.append(0)
        if hasattr(df_aux, 'AMOR') and not mt.isnan(df_aux['AMOR'].mean()):
            media_amor = df_aux['AMOR'].mean()
            array_amor.append(media_amor)
        else:
            array_amor.append(0)
        if hasattr(df_aux, 'NERVOSISMO') and not mt.isnan(df_aux['NERVOSISMO'].mean()):
            media_nervosismo = df_aux['NERVOSISMO'].mean()
            array_nervosismo.append(media_nervosismo)
        else:
            array_nervosismo.append(0)
        if hasattr(df_aux, 'OTIMISMO') and not mt.isnan(df_aux['OTIMISMO'].mean()):
            media_otimismo = df_aux['OTIMISMO'].mean()
            array_otimismo.append(media_otimismo)
        else:
            array_otimismo.append(0)
        if hasattr(df_aux, 'ORGULHO') and not mt.isnan(df_aux['ORGULHO'].mean()):
            media_orgulho = df_aux['ORGULHO'].mean()
            array_orgulho.append(media_orgulho)
        else:
            array_orgulho.append(0)
        if hasattr(df_aux, 'REALIZAÇÃO') and not mt.isnan(df_aux['REALIZAÇÃO'].mean()):
            media_realizacao = df_aux['REALIZAÇÃO'].mean()
            array_realizacao.append(media_realizacao)
        else:
            array_realizacao.append(0)
        if hasattr(df_aux, 'ALÍVIO') and not mt.isnan(df_aux['ALÍVIO'].mean()):
            media_alivio = df_aux['ALÍVIO'].mean()
            array_alivio.append(media_alivio)
        else:
            array_alivio.append(0)
        if hasattr(df_aux, 'REMORSO') and not mt.isnan(df_aux['REMORSO'].mean()):
            media_remorso = df_aux['REMORSO'].mean()
            array_remorso.append(media_remorso)
        else:
            array_remorso.append(0)
        if hasattr(df_aux, 'TRISTEZA') and not mt.isnan(df_aux['TRISTEZA'].mean()):
            media_tristeza = df_aux['TRISTEZA'].mean()
            array_tristeza.append(media_tristeza)
        else:
            array_tristeza.append(0)
        if hasattr(df_aux, 'SURPRESA') and not mt.isnan(df_aux['SURPRESA'].mean()):
            media_surpresa = df_aux['SURPRESA'].mean()
            array_surpresa.append(media_surpresa)
        else:
            array_surpresa.append(0)
        if hasattr(df_aux, 'NEUTRO') and not mt.isnan(df_aux['NEUTRO'].mean()):
            media_neutro = df_aux['NEUTRO'].mean()
            array_neutro.append(media_neutro)
        else:
            array_neutro.append(0)

        return array_admiracao, array_diversao, array_raiva, array_aborrecimento, array_aprovacao, array_cautela, array_confusao, array_curiosidade, array_desejo, array_desapontamento, array_desaprovacao, array_desgosto, array_constrangimento, array_empolgacao, array_medo, array_gratidao, array_sofrimento, array_alegria, array_amor, array_nervosismo, array_otimismo, array_orgulho, array_realizacao, array_alivio, array_remorso, array_tristeza, array_surpresa, array_neutro 

    def formata_data_data_frame(self, df):
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        df = df.sort_values(by=['data'])
        df['data'] = df['data'].map(self.formata_data)
        df = df.reset_index()
        df = df.drop(labels='index', axis=1)

        return df
    
    def formata_colunas_emocao_nrc_data_frame(self, df):
        for i, linha in df.iterrows():
            if hasattr(linha, 'CONFIANÇA'):
                df.at[i,'TEM_CONFIANÇA'] = 'CONFIANÇA'
            else:
                df.at[i,'TEM_CONFIANÇA'] = 'NONE'
            if hasattr(linha, 'ANSIEDADE'):
                df.at[i,'TEM_ANSIEDADE'] = 'ANSIEDADE'
            else:
                df.at[i,'TEM_ANSIEDADE'] = 'NONE'
            
        return df

    def formata_colunas_emocao_google_perspective_data_frame(self, df):
        for i, linha in df.iterrows():
            if linha.AMEAÇA != '0':
                df.at[i,'TEM_AMEAÇA'] = 'AMEAÇA'
            if linha.TOXICIDADE != '0':
                df.at[i,'TEM_TOXICIDADE'] = 'TOXICIDADE'
            if linha.PROFANIDADE != '0':
                df.at[i,'TEM_PROFANIDADE'] = 'PROFANIDADE'
            if linha.TOXICIDADE_SEVERA != '0':
                df.at[i,'TEM_TOXICIDADE_SEVERA'] = 'TOXICIDADE_SEVERA'
            if linha.ATAQUE_DE_IDENTIDADE != '0':
                df.at[i,'TEM_ATAQUE_DE_IDENTIDADE'] = 'ATAQUE_DE_IDENTIDADE'
            if linha.INSULTO != '0':
                df.at[i,'TEM_INSULTO'] = 'INSULTO'
        return df

    def formata_colunas_emocao_emo_roberta_data_frame(self, df):
        for i, linha in df.iterrows():
            if hasattr(linha, 'ADMIRAÇÃO'):
                df.at[i,'TEM_ADMIRAÇÃO'] = 'ADMIRAÇÃO'
            else:
                df.at[i,'TEM_ADMIRAÇÃO'] = 'NONE'
            if hasattr(linha, 'DIVERSÃO'):
                df.at[i,'TEM_DIVERSÃO'] = 'DIVERSÃO'
            else:
                df.at[i,'TEM_DIVERSÃO'] = 'NONE'
            if hasattr(linha, 'ABORRECIMENTO'):
                df.at[i,'TEM_ABORRECIMENTO'] = 'ABORRECIMENTO'
            else:
                df.at[i,'TEM_ABORRECIMENTO'] = 'NONE'
            if hasattr(linha, 'APROVAÇÃO'):
                df.at[i,'TEM_APROVAÇÃO'] = 'APROVAÇÃO'
            else:
                df.at[i,'TEM_APROVAÇÃO'] = 'NONE'
            if hasattr(linha, 'CAUTELA'):
                df.at[i,'TEM_CAUTELA'] = 'CAUTELA'
            else:
                df.at[i,'TEM_CAUTELA'] = 'NONE'
            if hasattr(linha, 'CONFUSÃO'):
                df.at[i,'TEM_CONFUSÃO'] = 'CONFUSÃO'
            else:
                df.at[i,'TEM_CONFUSÃO'] = 'NONE'
            if hasattr(linha, 'CURIOSIDADE'):
                df.at[i,'TEM_CURIOSIDADE'] = 'CURIOSIDADE'
            else:
                df.at[i,'TEM_CURIOSIDADE'] = 'NONE'
            if hasattr(linha, 'DESEJO'):
                df.at[i,'TEM_DESEJO'] = 'DESEJO'
            else:
                df.at[i,'TEM_DESEJO'] = 'NONE'
            if hasattr(linha, 'DESAPONTAMENTO'):
                df.at[i,'TEM_DESAPONTAMENTO'] = 'DESAPONTAMENTO'
            else:
                df.at[i,'TEM_DESAPONTAMENTO'] = 'NONE'
            if hasattr(linha, 'DESAPROVAÇÃO'):
                df.at[i,'TEM_DESAPROVAÇÃO'] = 'DESAPROVAÇÃO'
            else:
                df.at[i,'TEM_DESAPROVAÇÃO'] = 'NONE'
            if hasattr(linha, 'CONSTRANGIMENTO'):
                df.at[i,'TEM_CONSTRANGIMENTO'] = 'CONSTRANGIMENTO'
            else:
                df.at[i,'TEM_CONSTRANGIMENTO'] = 'NONE'
            if hasattr(linha, 'EMPOLGAÇÃO'):
                df.at[i,'TEM_EMPOLGAÇÃO'] = 'EMPOLGAÇÃO'
            else:
                df.at[i,'TEM_EMPOLGAÇÃO'] = 'NONE'
            if hasattr(linha, 'GRATIDÃO'):
                df.at[i,'TEM_GRATIDÃO'] = 'GRATIDÃO'
            else:
                df.at[i,'TEM_GRATIDÃO'] = 'NONE'
            if hasattr(linha, 'SOFRIMENTO'):
                df.at[i,'TEM_SOFRIMENTO'] = 'SOFRIMENTO'
            else:
                df.at[i,'TEM_SOFRIMENTO'] = 'NONE'
            if hasattr(linha, 'RAIVA'):
                df.at[i,'TEM_RAIVA'] = 'RAIVA'
            else:
                df.at[i,'TEM_RAIVA'] = 'NONE'
            if hasattr(linha, 'DESGOSTO'):
                df.at[i,'TEM_DESGOSTO'] = 'DESGOSTO'
            else:
                df.at[i,'TEM_DESGOSTO'] = 'NONE'
            if hasattr(linha, 'MEDO'):
                df.at[i,'TEM_MEDO'] = 'MEDO'
            else:
                df.at[i,'TEM_MEDO'] = 'NONE'
            if hasattr(linha, 'ALEGRIA'):
                df.at[i,'TEM_ALEGRIA'] = 'ALEGRIA'
            else:
                df.at[i,'TEM_ALEGRIA'] = 'NONE'
            if hasattr(linha, 'SURPRESA'):
                df.at[i,'TEM_SURPRESA'] = 'SURPRESA'
            else:
                df.at[i,'TEM_SURPRESA'] = 'NONE'
            if hasattr(linha, 'AMOR'):
                df.at[i,'TEM_AMOR'] = 'AMOR'
            else:
                df.at[i,'TEM_AMOR'] = 'NONE'
            if hasattr(linha, 'NERVOSISMO'):
                df.at[i,'TEM_NERVOSISMO'] = 'NERVOSISMO'
            else:
                df.at[i,'TEM_NERVOSISMO'] = 'NONE'
            if hasattr(linha, 'OTIMISMO'):
                df.at[i,'TEM_OTIMISMO'] = 'OTIMISMO'
            else:
                df.at[i,'TEM_OTIMISMO'] = 'NONE'
            if hasattr(linha, 'ORGULHO'):
                df.at[i,'TEM_ORGULHO'] = 'ORGULHO'
            else:
                df.at[i,'TEM_ORGULHO'] = 'NONE'
            if hasattr(linha, 'REALIZAÇÃO'):
                df.at[i,'TEM_REALIZAÇÃO'] = 'REALIZAÇÃO'
            else:
                df.at[i,'TEM_REALIZAÇÃO'] = 'NONE'
            if hasattr(linha, 'ALÍVIO'):
                df.at[i,'TEM_ALÍVIO'] = 'ALÍVIO'
            else:
                df.at[i,'TEM_ALÍVIO'] = 'NONE'
            if hasattr(linha, 'REMORSO'):
                df.at[i,'TEM_REMORSO'] = 'REMORSO'
            else:
                df.at[i,'TEM_REMORSO'] = 'NONE'
            if hasattr(linha, 'TRISTEZA'):
                df.at[i,'TEM_TRISTEZA'] = 'TRISTEZA'
            else:
                df.at[i,'TEM_TRISTEZA'] = 'NONE'
            if hasattr(linha, 'NEUTRO'):
                df.at[i,'TEM_NEUTRO'] = 'NEUTRO'
            else:
                df.at[i,'TEM_NEUTRO'] = 'NONE'

        return df

    def criacao_data_frame_combos(self, df_combos, array_nome_nrc_emocoes, array_nome_google_emocoes, array_nome_emo_roberta_emocoes):
        array_nome_emocoes_combo = []
        
        for i in range(len(array_nome_nrc_emocoes)):
            if array_nome_nrc_emocoes[i] not in array_nome_emocoes_combo:
                if array_nome_nrc_emocoes[i] != 'None':
                    array_nome_emocoes_combo.append(array_nome_nrc_emocoes[i])

        for i in range(len(array_nome_emo_roberta_emocoes)):
            if array_nome_emo_roberta_emocoes[i] not in array_nome_emocoes_combo:
                if array_nome_emo_roberta_emocoes[i] != 'None':
                    array_nome_emocoes_combo.append(array_nome_emo_roberta_emocoes[i])

        for i in range(len(array_nome_google_emocoes)):
            if array_nome_google_emocoes[i] not in array_nome_emocoes_combo:
                if array_nome_google_emocoes[i] != 'None':
                    array_nome_emocoes_combo.append(array_nome_google_emocoes[i])

        data = {'EMOCOES_COMBO': array_nome_emocoes_combo}
        df_combos['EMOCOES_COMBO'] = data['EMOCOES_COMBO']

        df_combos_relatorio_geral = pd.DataFrame()
        array_nome_emocoes_combo.append('POLARIDADE')
        data = {'EMOCOES_COMBO': array_nome_emocoes_combo}
        df_combos_relatorio_geral['EMOCOES_COMBO'] = data['EMOCOES_COMBO']

        df_combos = df_combos.sort_values('EMOCOES_COMBO')['EMOCOES_COMBO'].reset_index()
        df_combos = df_combos.drop(labels='index', axis=1)

        df_combos_relatorio_geral = df_combos_relatorio_geral.sort_values('EMOCOES_COMBO')['EMOCOES_COMBO'].reset_index()
        df_combos_relatorio_geral = df_combos_relatorio_geral.drop(labels='index', axis=1)

        return df_combos, df_combos_relatorio_geral, data

    def prepara_dados_grafico_relatorio_geral(self, data, df):
        df_relatorio_geral = pd.DataFrame()

        #Arrays gerais
        array_alunos_adicionados, array_aluno, array_polaridade = [], [], []

        #Arrays Google Perspective
        array_profanidade, array_toxicidade_severa, array_ataque_de_identidade, array_ameaca = [], [], [], []
        array_toxicidade, array_insulto = [], []
        
        #Arrays NRC Emotions
        array_ansiedade, array_confiança = [], []

        #Arrays Emo Roberta
        array_admiracao, array_diversao, array_raiva, array_aborrecimento, array_aprovacao = [], [], [], [], []
        array_cautela, array_confusao, array_curiosidade, array_desejo, array_desapontamento = [], [], [], [], []
        array_desaprovacao, array_desgosto, array_constrangimento, array_empolgacao, array_medo = [], [], [], [], []
        array_gratidao, array_sofrimento, array_alegria, array_amor, array_nervosismo = [], [], [], [], []
        array_otimismo, array_orgulho, array_realizacao, array_alivio, array_remorso = [], [], [], [], []
        array_tristeza, array_surpresa, array_neutro = [], [], []

        count_alunos = 0

        for index, aluno in enumerate(df['idUsuario'].values):
            if index == 0:
                array_alunos_adicionados.append(aluno)

                array_retorno_polaridade = self.prepara_df_grafico_relatorio_geral_polaridade(aluno, df)
                array_retorno_ansiedade, array_retorno_confiança = self.prepara_df_grafico_relatorio_geral_nrc_emo(aluno, df)
                array_retorno_profanidade, array_retorno_toxicidade_severa, array_retorno_ataque_de_identidade, array_retorno_ameaca, array_retorno_toxicidade, array_retorno_insulto = self.prepara_df_grafico_relatorio_geral_google_perspective(aluno, df)
                array_retorno_admiracao, array_retorno_diversao, array_retorno_raiva, array_retorno_aborrecimento, array_retorno_aprovacao, array_retorno_cautela, array_retorno_confusao, array_retorno_curiosidade, array_retorno_desejo, array_retorno_desapontamento, array_retorno_desaprovacao, array_retorno_desgosto, array_retorno_constrangimento, array_retorno_empolgacao, array_retorno_medo, array_retorno_gratidao, array_retorno_sofrimento, array_retorno_alegria, array_retorno_amor, array_retorno_nervosismo, array_retorno_otimismo, array_retorno_orgulho, array_retorno_realizacao, array_retorno_alivio, array_retorno_remorso, array_retorno_tristeza, array_retorno_surpresa, array_retorno_neutro = self.prepara_df_grafico_relatorio_geral_emo_roberta(aluno, df)
                
                array_aluno.append(count_alunos)
                count_alunos += 1

                array_polaridade.extend(array_retorno_polaridade)

                array_profanidade.extend(array_retorno_profanidade)
                array_toxicidade_severa.extend(array_retorno_toxicidade_severa)
                array_ataque_de_identidade.extend(array_retorno_ataque_de_identidade)
                array_ameaca.extend(array_retorno_ameaca)
                array_toxicidade.extend(array_retorno_toxicidade)
                array_insulto.extend(array_retorno_insulto)

                array_ansiedade.extend(array_retorno_ansiedade)
                array_confiança.extend(array_retorno_confiança)
                
                array_admiracao.extend(array_retorno_admiracao)
                array_diversao.extend(array_retorno_diversao)
                array_raiva.extend(array_retorno_raiva)
                array_aborrecimento.extend(array_retorno_aborrecimento)
                array_aprovacao.extend(array_retorno_aprovacao)
                array_cautela.extend(array_retorno_cautela)
                array_confusao.extend(array_retorno_confusao)
                array_curiosidade.extend(array_retorno_curiosidade)
                array_desejo.extend(array_retorno_desejo)
                array_desapontamento.extend(array_retorno_desapontamento)
                array_desaprovacao.extend(array_retorno_desaprovacao)
                array_desgosto.extend(array_retorno_desgosto)
                array_constrangimento.extend(array_retorno_constrangimento)
                array_empolgacao.extend(array_retorno_empolgacao)
                array_medo.extend(array_retorno_medo)
                array_gratidao.extend(array_retorno_gratidao)
                array_sofrimento.extend(array_retorno_sofrimento)
                array_alegria.extend(array_retorno_alegria)
                array_amor.extend(array_retorno_amor)
                array_nervosismo.extend(array_retorno_nervosismo)
                array_otimismo.extend(array_retorno_otimismo)
                array_orgulho.extend(array_retorno_orgulho)
                array_realizacao.extend(array_retorno_realizacao)
                array_alivio.extend(array_retorno_alivio)
                array_remorso.extend(array_retorno_remorso)
                array_tristeza.extend(array_retorno_tristeza)
                array_surpresa.extend(array_retorno_surpresa)
                array_neutro.extend(array_retorno_neutro)
            else:
                if aluno not in array_alunos_adicionados:
                    array_alunos_adicionados.append(aluno)

                    array_retorno_polaridade = self.prepara_df_grafico_relatorio_geral_polaridade(aluno, df)
                    array_retorno_ansiedade, array_retorno_confiança = self.prepara_df_grafico_relatorio_geral_nrc_emo(aluno, df)
                    array_retorno_profanidade, array_retorno_toxicidade_severa, array_retorno_ataque_de_identidade, array_retorno_ameaca, array_retorno_toxicidade, array_retorno_insulto = self.prepara_df_grafico_relatorio_geral_google_perspective(aluno, df)
                    array_retorno_admiracao, array_retorno_diversao, array_retorno_raiva, array_retorno_aborrecimento, array_retorno_aprovacao, array_retorno_cautela, array_retorno_confusao, array_retorno_curiosidade, array_retorno_desejo, array_retorno_desapontamento, array_retorno_desaprovacao, array_retorno_desgosto, array_retorno_constrangimento, array_retorno_empolgacao, array_retorno_medo, array_retorno_gratidao, array_retorno_sofrimento, array_retorno_alegria, array_retorno_amor, array_retorno_nervosismo, array_retorno_otimismo, array_retorno_orgulho, array_retorno_realizacao, array_retorno_alivio, array_retorno_remorso, array_retorno_tristeza, array_retorno_surpresa, array_retorno_neutro = self.prepara_df_grafico_relatorio_geral_emo_roberta(aluno, df)
                    
                    array_aluno.append(count_alunos)
                    count_alunos += 1

                    array_polaridade.extend(array_retorno_polaridade)

                    array_profanidade.extend(array_retorno_profanidade)
                    array_toxicidade_severa.extend(array_retorno_toxicidade_severa)
                    array_ataque_de_identidade.extend(array_retorno_ataque_de_identidade)
                    array_ameaca.extend(array_retorno_ameaca)
                    array_toxicidade.extend(array_retorno_toxicidade)
                    array_insulto.extend(array_retorno_insulto)

                    array_ansiedade.extend(array_retorno_ansiedade)
                    array_confiança.extend(array_retorno_confiança)
                    
                    array_admiracao.extend(array_retorno_admiracao)
                    array_diversao.extend(array_retorno_diversao)
                    array_raiva.extend(array_retorno_raiva)
                    array_aborrecimento.extend(array_retorno_aborrecimento)
                    array_aprovacao.extend(array_retorno_aprovacao)
                    array_cautela.extend(array_retorno_cautela)
                    array_confusao.extend(array_retorno_confusao)
                    array_curiosidade.extend(array_retorno_curiosidade)
                    array_desejo.extend(array_retorno_desejo)
                    array_desapontamento.extend(array_retorno_desapontamento)
                    array_desaprovacao.extend(array_retorno_desaprovacao)
                    array_desgosto.extend(array_retorno_desgosto)
                    array_constrangimento.extend(array_retorno_constrangimento)
                    array_empolgacao.extend(array_retorno_empolgacao)
                    array_medo.extend(array_retorno_medo)
                    array_gratidao.extend(array_retorno_gratidao)
                    array_sofrimento.extend(array_retorno_sofrimento)
                    array_alegria.extend(array_retorno_alegria)
                    array_amor.extend(array_retorno_amor)
                    array_nervosismo.extend(array_retorno_nervosismo)
                    array_otimismo.extend(array_retorno_otimismo)
                    array_orgulho.extend(array_retorno_orgulho)
                    array_realizacao.extend(array_retorno_realizacao)
                    array_alivio.extend(array_retorno_alivio)
                    array_remorso.extend(array_retorno_remorso)
                    array_tristeza.extend(array_retorno_tristeza)
                    array_surpresa.extend(array_retorno_surpresa)
                    array_neutro.extend(array_retorno_neutro)

        data['idUsuario'] = array_alunos_adicionados
        data['indiceUsuario'] = array_aluno
        data['polaridade'] = array_polaridade

        data['profanidade'] = array_profanidade
        data['toxicidade_severa'] = array_toxicidade_severa
        data['ataque_de_identidade'] = array_ataque_de_identidade
        data['ameaca'] = array_ameaca
        data['toxicidade'] = array_toxicidade
        data['insulto'] = array_insulto

        data['ansiedade'] = array_ansiedade
        data['confiança'] = array_confiança

        data['admiracao'] = array_admiracao
        data['diversao'] = array_diversao
        data['raiva'] = array_raiva
        data['aborrecimento'] = array_aborrecimento
        data['aprovacao'] = array_aprovacao
        data['cautela'] = array_cautela
        data['confusao'] = array_confusao
        data['curiosidade'] = array_curiosidade
        data['desejo'] = array_desejo
        data['desapontamento'] = array_desapontamento
        data['desaprovacao'] = array_desaprovacao
        data['desgosto'] = array_desgosto
        data['constrangimento'] = array_constrangimento
        data['empolgacao'] = array_empolgacao
        data['medo'] = array_medo
        data['gratidao'] = array_gratidao
        data['sofrimento'] = array_sofrimento
        data['alegria'] = array_alegria
        data['amor'] = array_amor
        data['nervosismo'] = array_nervosismo
        data['otimismo'] = array_otimismo
        data['orgulho'] = array_orgulho
        data['realizacao'] = array_realizacao
        data['alivio'] = array_alivio
        data['remorso'] = array_remorso
        data['tristeza'] = array_tristeza
        data['surpresa'] = array_surpresa
        data['neutro'] = array_neutro

        df_relatorio_geral['idUsuario'] = data['idUsuario']
        df_relatorio_geral['indiceUsuario'] = data['indiceUsuario']
        df_relatorio_geral['polaridade'] = data['polaridade']

        df_relatorio_geral['profanidade'] = data['profanidade']
        df_relatorio_geral['toxicidade_severa'] = data['toxicidade_severa']
        df_relatorio_geral['ataque_de_identidade'] = data['ataque_de_identidade']
        df_relatorio_geral['ameaça'] = data['ameaca']
        df_relatorio_geral['toxicidade'] = data['toxicidade']
        df_relatorio_geral['insulto'] = data['insulto']

        df_relatorio_geral['ansiedade'] = data['ansiedade'] 
        df_relatorio_geral['confiança'] = data['confiança'] 

        df_relatorio_geral['admiração'] = data['admiracao']
        df_relatorio_geral['diversão'] = data['diversao']
        df_relatorio_geral['raiva'] = data['raiva']
        df_relatorio_geral['aborrecimento'] = data['aborrecimento']
        df_relatorio_geral['aprovação'] = data['aprovacao']
        df_relatorio_geral['cautela'] = data['cautela']
        df_relatorio_geral['confusão'] = data['confusao']
        df_relatorio_geral['curiosidade'] = data['curiosidade']
        df_relatorio_geral['desejo'] = data['desejo']
        df_relatorio_geral['desapontamento'] = data['desapontamento']
        df_relatorio_geral['desaprovação'] = data['desaprovacao']
        df_relatorio_geral['desgosto'] = data['desgosto']
        df_relatorio_geral['constrangimento'] = data['constrangimento']
        df_relatorio_geral['empolgação'] = data['empolgacao']
        df_relatorio_geral['medo'] = data['medo']
        df_relatorio_geral['gratidão'] = data['gratidao']
        df_relatorio_geral['sofrimento'] = data['sofrimento']
        df_relatorio_geral['alegria'] = data['alegria']
        df_relatorio_geral['amor'] = data['amor']
        df_relatorio_geral['nervosismo'] = data['nervosismo']
        df_relatorio_geral['otimismo'] = data['otimismo']
        df_relatorio_geral['orgulho'] = data['orgulho']
        df_relatorio_geral['realização'] = data['realizacao']
        df_relatorio_geral['alívio'] = data['alivio']
        df_relatorio_geral['remorso'] = data['remorso']
        df_relatorio_geral['tristeza'] = data['tristeza']
        df_relatorio_geral['surpresa'] = data['surpresa']
        df_relatorio_geral['neutro'] = data['neutro']

        return df_relatorio_geral

    def traduz_emocoes_emo_roberta(self, emocao):
        if emocao == 'admiration':
            return 'Admiração'
        if emocao == 'amusement':
            return 'Diversão'
        if emocao == 'annoyance':
            return 'Aborrecimento'
        if emocao == 'approval':
            return 'Aprovação'
        if emocao == 'caring':
            return 'Cautela'
        if emocao == 'confusion':
            return 'Confusão' 
        if emocao == 'curiosity':
            return 'Curiosidade' 
        if emocao == 'desire':
            return 'Desejo' 
        if emocao == 'disappointment':
            return 'Desapontamento' 
        if emocao == 'disapproval':
            return 'Desaprovação' 
        if emocao == 'embarrassment':
            return 'Constrangimento' 
        if emocao == 'excitement':
            return 'Empolgação' 
        if emocao == 'gratitude':
            return 'Gratidão' 
        if emocao == 'grief':
            return 'Sofrimento' 
        if emocao == 'anger':   # Já tem na nrc
            return 'Raiva'
        if emocao == 'disgust': # Já tem na nrc
            return 'Desgosto' 
        if emocao == 'fear': # Já tem na nrc
            return 'Medo' 
        if emocao == 'joy':     # Já tem na nrc
            return 'Alegria' 
        if emocao == 'surprise': # Já tem na nrc
            return 'Surpresa'
        if emocao == 'love':
            return 'Amor' 
        if emocao == 'nervousness':
            return 'Nervosismo'
        if emocao == 'optimism':
            return 'Otimismo'
        if emocao == 'pride':
            return 'Orgulho'
        if emocao == 'realization':
            return 'Realização'
        if emocao == 'relief':
            return 'Alívio'
        if emocao == 'remorse':
            return 'Remorso'
        if emocao == 'sadness':
            return 'Tristeza'
        if emocao == 'neutral':
            return 'Neutro'

    def formata_emo_roberta(self, emotion):
        dicionario_retorno = {}

        if emotion != 'None':
            if '*' in emotion:
                todas_emocoes = emotion.split('*')
                for unica_emocao in todas_emocoes:
                    if unica_emocao != '':
                        nome_emocao = unica_emocao.split(':')[0]
                        valor_emocao = unica_emocao.split(':')[1]

                        nome_emocao = self.traduz_emocoes_nrc(nome_emocao)

                        dicionario_retorno[nome_emocao.upper()] = valor_emocao
            else:
                nome_emocao = emotion.split(':')[0]
                valor_emocao = emotion.split(':')[1]

                nome_emocao = self.traduz_emocoes_emo_roberta(nome_emocao)

                dicionario_retorno[nome_emocao.upper()] = valor_emocao

        return dicionario_retorno

    def prepara_dados_gerais_graficos(self, port):
        df = pd.read_csv('./data/dados_metricas_finais.csv', sep='-', index_col=False)
        df = self.formata_data_data_frame(df)
        df['polaridade'] = pd.to_numeric(df['polaridade'])

        # ------- INÍCIO TRATAMENTO NRC EMOTIONS -------

        retorno_nrc_emocoes = df['NRC_EMOTIONS'].map(self.formata_nrc_emotions)
        array_nome_nrc_emocoes = []
        dict_nrc_emocoes = {}

        for dados in retorno_nrc_emocoes:
            if len(dados) != 0:
                for nrc_emocao in dados:
                    if nrc_emocao not in array_nome_nrc_emocoes:
                        array_nome_nrc_emocoes.append(nrc_emocao)
                        dict_nrc_emocoes[nrc_emocao] = []

        #Pra fechar o numero de linhas do dataframe
        while len(array_nome_nrc_emocoes) < len(df.index):
            array_nome_nrc_emocoes.append('None')

        for i, dados in enumerate(retorno_nrc_emocoes):
            if len(dados) != 0:
                for nrc_emocao in dados:
                    dict_nrc_emocoes[nrc_emocao].append(float(dados[nrc_emocao]))
                for emocao in array_nome_nrc_emocoes:
                    if emocao != 'None':
                        while len(dict_nrc_emocoes[emocao]) < i + 1:
                            dict_nrc_emocoes[emocao].append(0)
            else:
                for chave in dict_nrc_emocoes.keys():
                    dict_nrc_emocoes[chave].append(0)

        #NRC - Tratamento valores de cada emoção (1 coluna pra cada)
        for emocao_nrc in array_nome_nrc_emocoes:
            if emocao_nrc != 'None':
                df[emocao_nrc] = dict_nrc_emocoes[emocao_nrc]   

        #NRC - Cria colunas para saber qual linha tem determinada emoção
        df = self.formata_colunas_emocao_nrc_data_frame(df)
        df = df.drop(labels='NRC_EMOTIONS', axis=1)

        # ------- FIM TRATAMENTO NRC EMOTIONS -------

        # ------- INÍCIO TRATAMENTO GOOGLE EMOTIONS -------

        retorno_google_emocoes = df['GooglePerspectiveMetrics'].map(self.formata_google_emotions)
        array_nome_google_emocoes = []
        dict_google_emocoes = {}

        for dados in retorno_google_emocoes:
            if len(dados) != 0:
                for google_emocao in dados:
                    if google_emocao.upper() not in array_nome_google_emocoes:
                        array_nome_google_emocoes.append(google_emocao.upper())
                        dict_google_emocoes[google_emocao.upper()] = []

        #Pra fechar o numero de linhas do dataframe
        while len(array_nome_google_emocoes) < len(df.index):
            array_nome_google_emocoes.append('None')

        for i, dados in enumerate(retorno_google_emocoes):
            if len(dados) != 0:
                for google_emocao in dados:
                    dict_google_emocoes[google_emocao.upper()].append(float(dados[google_emocao]))
                for emocao in array_nome_google_emocoes:
                    if emocao != 'None':
                        while len(dict_google_emocoes[emocao]) < i + 1:
                            dict_google_emocoes[emocao.upper()].append(0)
            else:
                for chave in dict_google_emocoes.keys():
                    dict_google_emocoes[chave.upper()].append(0)
                    
        #GOOGLE_EMOTIONS - Tratamento valores de cada emoção (1 coluna pra cada)
        for emocao_google in array_nome_google_emocoes:
            if emocao_google != 'None':
                df[emocao_google] = dict_google_emocoes[emocao_google]   

        #Google Perspective - Cria colunas para saber qual linha tem determinada emoção
        df = self.formata_colunas_emocao_google_perspective_data_frame(df)
        
        # ------- FIM TRATAMENTO GOOGLE EMOTIONS -------

        # ------- INICIO TRATAMENTO EMO ROBERTA -------

        #Pega emoções da EMO_ROBERTA
        retorno_emo_roberta = df['EMO_ROBERTA'].map(self.formata_emo_roberta)
        array_nome_emo_roberta_emocoes = []
        dict_emo_roberta_emocoes = {}

        for dados in retorno_emo_roberta:
            if len(dados) != 0:
                for roberta_emocao in dados:
                    if roberta_emocao.upper() not in array_nome_emo_roberta_emocoes:
                        array_nome_emo_roberta_emocoes.append(roberta_emocao.upper())
                        dict_emo_roberta_emocoes[roberta_emocao.upper()] = []

        while len(array_nome_emo_roberta_emocoes) < len(df.index):
            array_nome_emo_roberta_emocoes.append('None')

        for i, dados in enumerate(retorno_emo_roberta):
            if len(dados) != 0:
                for roberta_emocao in dados:
                    dict_emo_roberta_emocoes[roberta_emocao.upper()].append(float(dados[roberta_emocao]))
                for emocao in array_nome_emo_roberta_emocoes:
                    if emocao in dict_emo_roberta_emocoes:
                        if emocao != 'None':
                            while len(dict_emo_roberta_emocoes[emocao]) < i + 1:
                                dict_emo_roberta_emocoes[emocao.upper()].append(0) #np.nan  
            else:
                for chave in dict_emo_roberta_emocoes.keys():
                    dict_emo_roberta_emocoes[chave.upper()].append(0) #np.nan

        for emocao_roberta in array_nome_emo_roberta_emocoes:
                if emocao_roberta in dict_emo_roberta_emocoes:
                    df[emocao_roberta] = dict_emo_roberta_emocoes[emocao_roberta]  

        #Emo Roberta - Cria colunas para saber qual linha tem determinada emoção
        df = self.formata_colunas_emocao_emo_roberta_data_frame(df)

        # ------- FIM TRATAMENTO EMO ROBERTA -------

        #Cria dataFrame para o combo de emoções
        df_combos = pd.DataFrame()
        df_combos, df_combos_relatorio_geral, data = self.criacao_data_frame_combos(df_combos, array_nome_nrc_emocoes, array_nome_google_emocoes, array_nome_emo_roberta_emocoes)

        #Para utilizar no filtro de data
        if len(df['data']) > 0:
            dataInicial = df['data'][0].split('/')
            dataInicial = date(int(dataInicial[2]), int(dataInicial[1]), int(dataInicial[0]))

            dataFinal = df['data'][len(df['data']) - 1].split('/')
            dataFinal = date(int(dataFinal[2]), int(dataFinal[1]), int(dataFinal[0]))
        else:
            dataInicial = ''
            dataFinal = ''

        #Prepara os dados para serem utilizados no gráfico de relatório geral
        df_relatorio_geral = self.prepara_dados_grafico_relatorio_geral(data, df)

        self.ultima_emocao_analisada = ''
        self.b_clicou_ultimo_grafico = False

        self.inicializa_graficos(df, dataInicial, dataFinal, df_combos, df_combos_relatorio_geral, df_relatorio_geral, port)

    def inicializa_graficos(self, df, dataInicial, dataFinal, df_combos, df_combos_relatorio_geral, df_relatorio_geral, port):
        app = dash.Dash(
            __name__,external_stylesheets=['https://use.fontawesome.com/releases/v5.7.2/css/all.css'],

            meta_tags=[
                {'charset': 'utf-8'},
                {'name':'viewport','content':'width=device-width, initial-scale=1.0, shrink-to-fit=no'}
            ],
        )

        app.layout = html.Div([

            #Primeiro gráfico

            html.Div([

                html.Div([
                    html.I(className='far fa-address-card', style={'font-size':'36px', 'margin-left': '170%', 'margin-top': '46%'}),
                ],className='one column'),

                html.Div([
                    
                    html.Label(
                        ['Escolha o Aluno:'],
                        style={'font-weight': 'bold', 'text-align': 'left'},
                    ),
                    dcc.Dropdown(id='cboAlunoPolaridade',
                        options=[{'label':x, 'value':x} for x in df.sort_values('idUsuario')['idUsuario'].unique()], #df['usuario'].unique()
                        value=df['idUsuario'][0] if len(df['idUsuario']) > 0 else '', #Deve ta vindo vazio dai n funciona print ("par" if x % 2 == 0 else "impar")
                        multi=False,
                        disabled=False,
                        clearable=True,
                        searchable=True,
                        placeholder='Escolha o Aluno...',
                        className='form-dropdown',
                        style={'width':"90%"},
                        persistence='string',
                        persistence_type='memory'),
                ],className='two columns margin-Left'),

                html.Div([
                    html.I(className='far fa-calendar-check', style={'font-size':'36px', 'margin-left': '140%', 'margin-top': '46%'}),
                ],className='one column'),

                html.Div([
                    html.Label(['Escolha o período:'],style={'font-weight': 'bold', 'text-align': 'left'}),
                    dcc.DatePickerRange(
                        id="dateRangePolaridade",
                        min_date_allowed='',
                        max_date_allowed='',
                        start_date=dataInicial,
                        end_date=dataFinal,
                        display_format='DD/MM/YYYY'
                    ),
                ],className='four columns padding-1P'),

            ],className='twelve columns div-fields'),

            html.Div([
                html.Br(),
                dcc.Graph(id='grafico_polaridade')
            ],className='eight columns'),

            html.Div([
                html.Label(['Mensagem selecionada:'],style={'font-weight': 'bold', 'text-align': 'center'}),
                html.Div(
                    id='textAreaMsgsPolaridade',
                    style={'width': '95%', 'height': '450px', 'min-width': '120px', 'min-height': '90px', 'max-width': '400px', 'max-height': '470px', 'padding': '1px', 'border': '1px solid rgb(169, 169, 169)', 'overflow-y': 'auto', 'resize': 'both', 'background-color': 'rgb(235, 235, 228)' },
                ),
            ],className='three columns margin-Top'),

            html.Div([
                html.Br()
            ], className='twelve columns border-bottom'),

            #Fim primeiro gráfico

            #Segundo Gráfico

            html.Div([

                html.Div([
                    html.I(className='far fa-address-card', style={'font-size':'36px', 'margin-left': '170%', 'margin-top': '46%'}),
                ],className='one column'),

                html.Div([
                    
                    html.Label(
                        ['Escolha o(s) Aluno(s):'],
                        style={'font-weight': 'bold', 'text-align': 'left'},
                    ),
                    dcc.Dropdown(id='cboAlunos',
                        options=[{'label':x, 'value':x} for x in df.sort_values('idUsuario')['idUsuario'].unique()], #df['usuario'].unique()
                        value=df['idUsuario'][0] if len(df['idUsuario']) > 0 else '',
                        multi=True,
                        disabled=False,
                        clearable=True,
                        searchable=True,
                        placeholder='Escolha o(s) Aluno(s)...',
                        className='form-dropdown',
                        style={'width':'90%'},
                        persistence='string',
                        persistence_type='memory'),
                ],className='two columns margin-Left'),

                html.Div([
                    html.I(className='far fa-calendar-check', style={'font-size':'36px', 'margin-left': '140%', 'margin-top': '46%'}),
                ],className='one column'),

                html.Div([
                    html.Label(['Escolha o período:'],style={'font-weight': 'bold', 'text-align': 'left'}),
                    dcc.DatePickerRange(
                        id="dateRangeMetricas",
                        min_date_allowed='',
                        max_date_allowed='',
                        start_date=dataInicial,
                        end_date=dataFinal,
                        display_format='DD/MM/YYYY',
                    ),
                ],className='three columns fake padding-1P'),

                html.Div([
                    html.I(className='far fa-smile', style={'font-size':'36px', 'margin-left': '170%', 'margin-top': '46%'}),
                ],className='one column'),

                html.Div([
                    html.Label(['Escolha uma métrica:'],style={'font-weight': 'bold', 'text-align': 'left'}),
                    dcc.Dropdown(id='cboMetricas',
                        options=[{'label':x, 'value':x} for x in df_combos.sort_values('EMOCOES_COMBO')['EMOCOES_COMBO'].unique()], #df['usuario'].unique()
                        value=df_combos['EMOCOES_COMBO'][0] if len(df_combos['EMOCOES_COMBO']) > 0 else '',
                        multi=False,
                        disabled=False,
                        clearable=True,
                        searchable=True,
                        placeholder='Escolha uma Métrica...',
                        className='form-dropdown',
                        style={'width':"100%"},
                        persistence='string',
                        persistence_type='memory'),
                ],className='two columns fake margin-Left'),
            ],className='twelve columns div-fields'),

            html.Div([
                html.Br(),
                dcc.Graph(id='grafico_metricas')
            ],className='eight columns'),

            html.Div([
                html.Label(['Mensagem selecionada:'],style={'font-weight': 'bold', 'text-align': 'center'}),
                html.Div(
                    id='divMetricasFakeTextArea', 
                    style={'width': '95%', 'height': '470px', 'min-width': '120px', 'min-height': '90px', 'max-width': '400px', 'max-height': '470px', 'padding': '1px', 'border': '1px solid rgb(169, 169, 169)', 'overflow-y': 'auto', 'resize': 'both', 'background-color': 'rgb(235, 235, 228)' }
                ),
            ],className='three columns margin-Top'),

            html.Div([
                dcc.ConfirmDialog(
                    id='alertaSemMensagens',
                    message='Não há mensagens para o curso selecionado.',
                ),
            ]),

            html.Div([
                html.Br()
            ], className='twelve columns border-bottom'),

            #Fim segundo gráfico

            #Terceiro Gráfico

            html.Div([
                html.Div([
                    html.I(className='far fa-smile', style={'font-size':'36px', 'margin-left': '170%', 'margin-top': '46%'}),
                ],className='one column'),

                html.Div([
                    html.Label(['Escolha uma métrica:'],style={'font-weight': 'bold', 'text-align': 'left'}),
                    dcc.Dropdown(id='cboMetricasRelatorioGeral',
                        options=[{'label':x, 'value':x} for x in df_combos_relatorio_geral.sort_values('EMOCOES_COMBO')['EMOCOES_COMBO'].unique()], #df['usuario'].unique()
                        value=df_combos_relatorio_geral['EMOCOES_COMBO'][0] if len(df_combos_relatorio_geral['EMOCOES_COMBO']) > 0 else '',
                        multi=False,
                        disabled=False,
                        clearable=True,
                        searchable=True,
                        placeholder='Escolha uma Métrica...',
                        className='form-dropdown',
                        style={'width':"100%"},
                        persistence='string',
                        persistence_type='memory'),
                ],className='two columns fake margin-Left'),
            ],className='twelve columns div-fields'),

            html.Div([
                html.Br(),
                dcc.Graph(id='grafico_relatorio_geral')
            ],className='twelve columns'),

            html.Div([
                dcc.ConfirmDialog(
                    id='alertaColunaSelecionada',
                    message='Os filtros dos gráficos acima serão preenchidos de acordo com o usuário e métrica selecionados.',
                ),
            ]),

            #Fim Terceiro Gráfico
        
        ])

        @app.callback(
            [
                Output('grafico_polaridade','figure'),
                Output('textAreaMsgsPolaridade', 'children'),
            ],
            [
                Input('grafico_polaridade', 'clickData'),
                Input('cboAlunoPolaridade','value'),
                Input('dateRangePolaridade', 'start_date'),
                Input('dateRangePolaridade', 'end_date'),
                State('textAreaMsgsPolaridade', 'children')
            ]
        )

        def atualiza_grafico_polaridade(clickData, aluno, start_date, end_date, children):
            df_date = pd.DataFrame()
            df_date['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
            df_date = df_date.sort_values(by=['data'])

            dff = df[(df['idUsuario'] == aluno) & (df_date['data'] >= start_date) & (df_date['data'] <= end_date)]
            
            if len(dff['polaridade']) > 0:
                cores = []
                for polaridade in dff['polaridade']:
                    if float(polaridade) >= 0:
                        cores.append('green')
                    else:
                        cores.append('red')

                dff.insert(2, 'cores_polaridade', cores, True)

                fig = px.bar(dff, x=dff['data'], y=dff['polaridade'], 
                    color=dff['cores_polaridade'],
                    color_discrete_map={
                        'green': 'green',
                        'red': 'red'
                    },
                    labels=dict(data="DATA", polaridade="POLARIDADE"),
                    title='Visualização da Métrica \'Polaridade\' por Aluno', 
                    height=600)
                
                valor_minimo = dff['polaridade'].min() 
                if float(valor_minimo) < 0:
                    valor_minimo = valor_minimo - 0.1
                else:
                    valor_minimo = 0

                valor_maximo = dff['polaridade'].max()
                if float(valor_maximo) < 1:
                    valor_maximo = 1 

                fig.update_layout(title_text='Visualização da Métrica \'Polaridade\' por Aluno', 
                    title_x=0.5, 
                    yaxis_range=[valor_minimo,valor_maximo + 0.1])

                fig.update_layout({
                    'showlegend':False,
                })

                #Tratamento pro Click do ponto
                gValorTexto = ''
                gCabecalhoTexto = ''
                gStringClassificacao = ''
                datas_mensagens_procuradas = []

                if clickData is not None:
                    for indicePoints in range(len(clickData['points'])):
                        datas_mensagens_procuradas = clickData['points'][indicePoints]['x']

                    vet_alunos_mensagens_verificadas = []
                    vet_mensagens_verificadas = []

                    df_filtrado_data_procurada = dff[dff['data'] == datas_mensagens_procuradas]
                    df_filtrado_data_procurada = df_filtrado_data_procurada.sort_values(by='polaridade', ascending=False)

                    for i, data_df in enumerate(df_filtrado_data_procurada['data'].values):
                        if df_filtrado_data_procurada['mensagem'].values[i] not in vet_mensagens_verificadas:
                                    vet_alunos_mensagens_verificadas.append(df_filtrado_data_procurada['idUsuario'].values[i])
                                    vet_mensagens_verificadas.append(df_filtrado_data_procurada['mensagem'].values[i])
                                    classificacoes = df_filtrado_data_procurada['classificacao'].values[i].split(',')
                                    gStringClassificacao = ''
                                    for j in range(len(classificacoes)):
                                        classificacao = classificacoes[j][1:].replace("'", "").upper()
                                        if(classificacao != ']'):
                                            gStringClassificacao += '[' + classificacao.replace(']', '') + ']'

                                    if len(vet_mensagens_verificadas) > 1:
                                        gCabecalhoTexto += '&nbsp;&nbsp;' + 'ALUNO ' + str(df_filtrado_data_procurada['idUsuario'].values[i]) + ' [' + str(round(df_filtrado_data_procurada['polaridade'].values[i], 4)) +'] : ' # + string_de_classificacao + ': '
                                    else:
                                        gCabecalhoTexto += 'ALUNO ' + str(df_filtrado_data_procurada['idUsuario'].values[i]) + ' [' + str(round(df_filtrado_data_procurada['polaridade'].values[i], 4)) +'] : '

                                    if len(vet_mensagens_verificadas) > 1:
                                        gValorTexto += '&nbsp;&nbsp;' + df_filtrado_data_procurada['mensagem'].values[i] 
                                    else:
                                        gValorTexto += df_filtrado_data_procurada['mensagem'].values[i]
                
                corClassificacao = ''
                indices_adicionados_classificacao_children = []

                if gStringClassificacao != '' and children != '':
                    vetClassificacao = gStringClassificacao.split(']')
                    classificacao_vetor = []
                    cor_classificacao = []
                    for i in range(len(vetClassificacao)):
                        if vetClassificacao[i] != '':
                            vetClassificacao[i] += ']'
                            if vetClassificacao[i] == '[AGRESSÃO]':
                                corClassificacao = 'red'
                            elif vetClassificacao[i] == '[RECLAMAÇÃO]' or vetClassificacao[i] == '[INSATISFAÇÃO]':
                                corClassificacao = 'orange'
                            elif vetClassificacao[i] == '[ELOGIO]' or vetClassificacao[i] == '[INTERESSE]':
                                corClassificacao = 'green'
                            elif vetClassificacao[i] == '[PREOCUPAÇÃO]':
                                corClassificacao = 'purple'
                            else:
                                corClassificacao = 'black'

                            classificacao_vetor.append(vetClassificacao[i])
                            cor_classificacao.append(corClassificacao)

                    nova_div_classificacao = html.Div(
                        children=[
                            html.Div(classificacao_vetor[i], style={'color': cor_classificacao[i], 'float': 'left'})
                            for i in range(len(classificacao_vetor))
                        ]
                    )

                    if children != '':
                        indices_adicionados_classificacao_children.append(len(children))
                        children.append(nova_div_classificacao)

                conteudo_classificacao = {}
                if len(indices_adicionados_classificacao_children) > 0:
                    for i in range(len(indices_adicionados_classificacao_children)):
                        if i == 0:
                            teste = children[indices_adicionados_classificacao_children[i]]
                        else:
                            teste.children.append(children[indices_adicionados_classificacao_children[i]])
                    conteudo_classificacao = teste

                indices_mensagens_adicionadas_children = [] #Zera os indices
                if '&nbsp;&nbsp;' in gValorTexto: #Se tem que quebrar linha entre as mensagens
                    gCabecalhoTexto = gCabecalhoTexto.split('&nbsp;&nbsp;')
                    gValorTexto = gValorTexto.split('&nbsp;&nbsp;')
                    for frase_selecionada in range(len(gValorTexto)):
                        indice_dataFrame_mensagem = dff[dff['mensagem'] == gValorTexto[frase_selecionada]].index.values.astype(int)[0]
                        classificacao_mensagem_atual = dff['classificacao'][indice_dataFrame_mensagem]
                        gStringClassificacao = ''

                        classificacoes = classificacao_mensagem_atual.split(',')
                        for j in range(len(classificacoes)):
                            classificacao = classificacoes[j][1:].replace("'", "").upper()
                            if(classificacao != ']'):
                                gStringClassificacao += '[' + classificacao.replace(']','') + ']'

                        if gStringClassificacao != '' and children != '':
                            vetClassificacao = gStringClassificacao.split(']')
                            classificacao_vetor = []
                            cor_classificacao = []
                            for i in range(len(vetClassificacao)):
                                if vetClassificacao[i] != '':
                                    vetClassificacao[i] += ']'
                                    if vetClassificacao[i] == '[AGRESSÃO]':
                                        corClassificacao = 'red'
                                    elif vetClassificacao[i] == '[RECLAMAÇÃO]' or vetClassificacao[i] == '[INSATISFAÇÃO]':
                                        corClassificacao = 'orange'
                                    elif vetClassificacao[i] == '[ELOGIO]' or vetClassificacao[i] == '[INTERESSE]':
                                        corClassificacao = 'green'
                                    elif vetClassificacao[i] == '[PREOCUPAÇÃO]':
                                        corClassificacao = 'purple'
                                    else:
                                        corClassificacao = 'black'

                                    classificacao_vetor.append(vetClassificacao[i])
                                    cor_classificacao.append(corClassificacao)
                                    
                            nova_div_classificacao = html.Div(
                                children=[
                                    html.Div(classificacao_vetor[i], style={'color': cor_classificacao[i], 'float': 'left'})
                                    for i in range(len(classificacao_vetor))
                                ]
                            )

                            div_separando_mensagens = html.Div(
                                children=[
                                    html.Div(gCabecalhoTexto[frase_selecionada], style={'color': 'black', 'font-weight': 'bold','float': 'left'}),
                                    nova_div_classificacao,
                                    html.Br(),
                                    html.Div(gValorTexto[frase_selecionada], style={})
                                ]
                            )

                            indices_mensagens_adicionadas_children.append(len(children))
                            children.append(div_separando_mensagens)
                        else:
                            if children != '':
                                div_separando_mensagens = html.Div(
                                    children=[
                                        html.Div(gCabecalhoTexto[frase_selecionada], style={'color': 'black', 'font-weight': 'bold','float': 'left'}),
                                        html.Br(),
                                        html.Div(gValorTexto[frase_selecionada], style={})
                                    ]
                                )

                                indices_mensagens_adicionadas_children.append(len(children))
                                children.append(div_separando_mensagens)

                conteudo_mensagem_mesmo_usuario = {}
                if len(indices_mensagens_adicionadas_children) > 0:
                    for i in range(len(indices_mensagens_adicionadas_children)):
                        if i == 0:
                            teste = children[indices_mensagens_adicionadas_children[i]]
                        else:
                            teste.children.append(children[indices_mensagens_adicionadas_children[i]])
                    conteudo_mensagem_mesmo_usuario = teste

                if len(indices_mensagens_adicionadas_children) > 0 : #Tratamento para caso de múltiplas mensagens de um mesmo usuário
                    new_div = html.Div(
                        children=[
                            html.Div(conteudo_mensagem_mesmo_usuario, style={}),
                            html.Br(),
                        ]
                    )
                else:
                    new_div = html.Div(
                        children=[
                            html.Div(gCabecalhoTexto, style={'color': 'black', 'font-weight': 'bold','float': 'left'}),
                            html.Div(conteudo_classificacao),
                            html.Br(),
                            html.Div(gValorTexto, style={}),
                            html.Br(),
                        ]
                    )

                return fig, new_div.children
            else:
                return '', ''

        @app.callback(
            [
                Output('grafico_metricas','figure'),
                Output('alertaSemMensagens', 'displayed'),
                Output('divMetricasFakeTextArea', 'children'),
            ],
            [
                Input('grafico_metricas', 'clickData'),
                Input('cboAlunos','value'),
                Input('cboMetricas','value'),
                Input('dateRangeMetricas', 'start_date'),
                Input('dateRangeMetricas', 'end_date'),
                State('divMetricasFakeTextArea', 'children')
            ]
        )

        def atualiza_grafico_metricas(clickData, alunos, nrc_emotion, start_date, end_date, children):
            dff_aux_alunos = ''

            if isinstance(alunos, int): #Caso for apenas um número
                dff_aux_alunos = df['idUsuario']==alunos
            else: #Caso forem múltiplas opções selecionadas
                if len(alunos) == 1: #Se tiver apenas uma opção selecionada
                    dff_aux_alunos = df['idUsuario']==alunos[0]
                else:
                    if len(alunos) == 0: #Caso nenhuma for selecionada, não exibe nada
                        alunos = 0
                        dff_aux_alunos = df['idUsuario']==alunos
                    else: #Caso tenha mais de uma, filtra
                        alunos_selecionados_df = []
                        vet_bool = []
                        for i, aluno in enumerate(alunos):
                            if i == 0:
                                vet_bool = (df['idUsuario']==aluno).values
                            else:
                                new_vet_bool = (df['idUsuario']==aluno).values
                                for indice, elem in enumerate(vet_bool):
                                    if (new_vet_bool[indice] != vet_bool[indice]) and new_vet_bool[indice] == True:
                                        vet_bool[indice] = True

                        dff_aux_alunos = vet_bool

            filtraPelaColuna = nrc_emotion
            if filtraPelaColuna == 'POLARIDADE':
                return '', False, '' 

            if filtraPelaColuna != '' and (not df.empty):
                df_date = pd.DataFrame()
                df_date['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
                df_date = df_date.sort_values(by=['data'])
                
                if nrc_emotion == None:
                    dff=df[dff_aux_alunos & (df_date['data'] >= start_date) & (df_date['data'] <= end_date)]
                else:
                    dff=df[dff_aux_alunos & (df['TEM_' + nrc_emotion.upper()]==nrc_emotion) & (df_date['data'] >= start_date) & (df_date['data'] <= end_date)]
                
                b_mostra_legenda = True
                if filtraPelaColuna in dff.columns:
                    dff = dff[dff[filtraPelaColuna].notnull()]
                else:
                    dff = pd.DataFrame()
                    dff['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
                    dff = dff.sort_values(by=['data'])
                    dff[filtraPelaColuna] = None
                    dff['idUsuario'] = None
                    b_mostra_legenda = False

                fig = px.line(dff, 
                    x='data', 
                    y=filtraPelaColuna, 
                    color='idUsuario', 
                    labels=dict(idUsuario="USUÁRIO(S)"),
                    height=600) 

                fig.update_traces(mode='markers', opacity=1.0, marker=dict(size=12))

                fig.update_layout(yaxis={'title':filtraPelaColuna.upper()},
                                xaxis={'title':'DATA'},
                                title={'text':'Visualização Métricas Gerais',
                                'font':{'size':20},'x':0.5,'xanchor':'center'},
                                yaxis_range=[0,1])

                if not b_mostra_legenda:
                    fig.update_layout({
                        'showlegend':False,
                    })

                #Tratamento pro Click do ponto
                gValorTexto = ''
                gCabecalhoTexto = ''
                gStringClassificacao = ''
                data_mensagens_procuradas = ''

                if clickData is not None and hasattr(dff, 'mensagem'):
                    for indicePoints in range(len(clickData['points'])):
                        data_mensagens_procuradas = clickData['points'][indicePoints]['x']

                    vet_alunos_mensagens_verificadas = []
                    vet_mensagens_verificadas = []

                    df_filtrado_data_procurada = dff[dff['data'] == data_mensagens_procuradas]
                    df_filtrado_data_procurada = df_filtrado_data_procurada.sort_values(by=filtraPelaColuna, ascending=False)

                    for i, data_df in enumerate(df_filtrado_data_procurada['data'].values):
                        if df_filtrado_data_procurada['mensagem'].values[i] not in vet_mensagens_verificadas:
                            vet_alunos_mensagens_verificadas.append(df_filtrado_data_procurada['idUsuario'].values[i])
                            vet_mensagens_verificadas.append(df_filtrado_data_procurada['mensagem'].values[i])
                            
                            classificacoes = df_filtrado_data_procurada['classificacao'].values[i].split(',')
                            gStringClassificacao = ''
                            for j in range(len(classificacoes)):
                                classificacao = classificacoes[j][1:].replace("'", "").upper()
                                if(classificacao != ']'):
                                    gStringClassificacao += '[' + classificacao.replace(']','') + ']'

                            if len(vet_mensagens_verificadas) > 1:
                                gCabecalhoTexto += '&nbsp;&nbsp;' + 'ALUNO ' + str(df_filtrado_data_procurada['idUsuario'].values[i]) + ' [' + str(round(df_filtrado_data_procurada[filtraPelaColuna].values[i], 4)) +'] : ' #' ' + gStringClassificacao +
                            else:
                                gCabecalhoTexto += 'ALUNO ' + str(df_filtrado_data_procurada['idUsuario'].values[i]) + ' [' + str(round(df_filtrado_data_procurada[filtraPelaColuna].values[i], 4)) +'] : '

                            if len(vet_mensagens_verificadas) > 1:
                                gValorTexto += '&nbsp;&nbsp;' + df_filtrado_data_procurada['mensagem'].values[i] 
                            else:
                                gValorTexto += df_filtrado_data_procurada['mensagem'].values[i]
          
                corClassificacao = ''
                indices_adicionados_classificacao_children = []

                if gStringClassificacao != '' and children != '':
                    vetClassificacao = gStringClassificacao.split(']')
                    classificacao_vetor = []
                    cor_classificacao = []
                    for i in range(len(vetClassificacao)):
                        if vetClassificacao[i] != '':
                            vetClassificacao[i] += ']'
                            if vetClassificacao[i] == '[AGRESSÃO]':
                                corClassificacao = 'red'
                            elif vetClassificacao[i] == '[RECLAMAÇÃO]' or vetClassificacao[i] == '[INSATISFAÇÃO]':
                                corClassificacao = 'orange'
                            elif vetClassificacao[i] == '[ELOGIO]' or vetClassificacao[i] == '[INTERESSE]':
                                corClassificacao = 'green'
                            elif vetClassificacao[i] == '[PREOCUPAÇÃO]':
                                corClassificacao = 'purple'
                            else:
                                corClassificacao = 'black'

                            classificacao_vetor.append(vetClassificacao[i])
                            cor_classificacao.append(corClassificacao)

                    nova_div_classificacao = html.Div(
                        children=[
                            html.Div(classificacao_vetor[i], style={'color': cor_classificacao[i], 'float': 'left'})
                            for i in range(len(classificacao_vetor))
                        ]
                    )

                    indices_adicionados_classificacao_children.append(len(children))
                    children.append(nova_div_classificacao)

                conteudo_classificacao = {}
                if len(indices_adicionados_classificacao_children) > 0:
                    for i in range(len(indices_adicionados_classificacao_children)):
                        if i == 0:
                            teste = children[indices_adicionados_classificacao_children[i]]
                        else:
                            teste.children.append(children[indices_adicionados_classificacao_children[i]])
                    conteudo_classificacao = teste

                new_div = ''
                count_new_div = 0
                indices_mensagens_adicionadas_children = [] #Zera os indices
                if '&nbsp;&nbsp;' in gValorTexto: #Se tem que quebrar linha entre as mensagens
                    gCabecalhoTexto = gCabecalhoTexto.split('&nbsp;&nbsp;')
                    gValorTexto = gValorTexto.split('&nbsp;&nbsp;')
                    for frase_selecionada in range(len(gValorTexto)):
                        indice_dataFrame_mensagem = dff[dff['mensagem'] == gValorTexto[frase_selecionada]].index.values.astype(int)[0]
                        classificacao_mensagem_atual = dff['classificacao'][indice_dataFrame_mensagem]
                        gStringClassificacao = ''

                        classificacoes = classificacao_mensagem_atual.split(',')
                        for j in range(len(classificacoes)):
                            classificacao = classificacoes[j][1:].replace("'", "").upper()
                            if(classificacao != ']'):
                                gStringClassificacao += '[' + classificacao.replace(']','') + ']'

                        if gStringClassificacao != '' and children != '':
                            vetClassificacao = gStringClassificacao.split(']')

                            classificacao_vetor = []
                            cor_classificacao = []

                            for i in range(len(vetClassificacao)):
                                if vetClassificacao[i] != '':
                                    vetClassificacao[i] += ']'
                                    if vetClassificacao[i] == '[AGRESSÃO]':
                                        corClassificacao = 'red'
                                    elif vetClassificacao[i] == '[RECLAMAÇÃO]' or vetClassificacao[i] == '[INSATISFAÇÃO]':
                                        corClassificacao = 'orange'
                                    elif vetClassificacao[i] == '[ELOGIO]' or vetClassificacao[i] == '[INTERESSE]':
                                        corClassificacao = 'green'
                                    elif vetClassificacao[i] == '[PREOCUPAÇÃO]':
                                        corClassificacao = 'purple'
                                    else:
                                        corClassificacao = 'black'

                                    classificacao_vetor.append(vetClassificacao[i])
                                    cor_classificacao.append(corClassificacao)

                            nova_div_classificacao = html.Div(
                                children=[
                                    html.Div(classificacao_vetor[i], style={'color': cor_classificacao[i], 'float': 'left'})
                                    for i in range(len(classificacao_vetor))
                                ]
                            )

                            div_separando_mensagens = html.Div(
                                children=[
                                    html.Div(gCabecalhoTexto[frase_selecionada], style={'color': 'black', 'font-weight': 'bold','float': 'left'}),
                                    nova_div_classificacao,
                                    html.Br(),
                                    html.Div(gValorTexto[frase_selecionada], style={})
                                ]
                            )

                            
                            if children != '':
                                indices_mensagens_adicionadas_children.append(len(children))
                                children.append(div_separando_mensagens)
                            else: 
                                if count_new_div == 0:
                                    new_div = div_separando_mensagens
                                    count_new_div += 1
                                else:
                                    new_div.children.append(div_separando_mensagens)
                        else:
                            div_separando_mensagens = html.Div(
                                children=[
                                    html.Div(gCabecalhoTexto[frase_selecionada], style={'color': 'black', 'font-weight': 'bold','float': 'left'}),
                                    html.Br(),
                                    html.Div(gValorTexto[frase_selecionada], style={})
                                ]
                            )

                            if children != '':
                                indices_mensagens_adicionadas_children.append(len(children))
                                children.append(div_separando_mensagens)
                            else:
                                if count_new_div == 0:
                                    new_div = div_separando_mensagens
                                    count_new_div += 1
                                else:
                                    new_div.children.append(div_separando_mensagens)
      
                conteudo_mensagem_mesmo_usuario = {}
                if len(indices_mensagens_adicionadas_children) > 0:
                    for i in range(len(indices_mensagens_adicionadas_children)):
                        if i == 0:
                            teste = children[indices_mensagens_adicionadas_children[i]]
                        else:
                            teste.children.append(children[indices_mensagens_adicionadas_children[i]])
                    conteudo_mensagem_mesmo_usuario = teste

                if len(indices_mensagens_adicionadas_children) > 0 : #Tratamento para caso de múltiplas mensagens de um mesmo usuário
                    new_div = html.Div(
                        children=[
                            html.Div(conteudo_mensagem_mesmo_usuario, style={}),
                            html.Br(),
                        ]
                    )
                else:
                    if type(gCabecalhoTexto) is str:
                        new_div = html.Div(
                            children=[
                                html.Div(gCabecalhoTexto, style={'color': 'black', 'font-weight': 'bold','float': 'left'}),
                                html.Div(conteudo_classificacao),
                                html.Br(),
                                html.Div(gValorTexto, style={}),
                                html.Br(),
                            ]
                        )
                    if len(gCabecalhoTexto) <= 1:
                        new_div = html.Div(
                            children=[
                                html.Div(gCabecalhoTexto, style={'color': 'black', 'font-weight': 'bold','float': 'left'}),
                                html.Div(conteudo_classificacao),
                                html.Br(),
                                html.Div(gValorTexto, style={}),
                                html.Br(),
                            ]
                        )

                #Se mudou a emoção, limpa as mensagens
                if clickData is not None:
                    if self.ultima_emocao_analisada == '':
                        self.ultima_emocao_analisada = filtraPelaColuna
                    else:
                        if self.ultima_emocao_analisada != filtraPelaColuna: 
                            self.ultima_emocao_analisada = filtraPelaColuna
                            return fig, False, ''

                return fig, False, new_div.children
            else:
                return '', True, '' 

        @app.callback(
            [
                Output('grafico_relatorio_geral','figure'),
                Output('cboAlunos', 'value'),
                Output('cboMetricas', 'value'),
                Output('cboAlunoPolaridade', 'value'),
                Output('grafico_relatorio_geral', 'clickData'),
                Output('alertaColunaSelecionada', 'displayed'),
            ],
            [
                Input('grafico_relatorio_geral', 'clickData'),
                Input('cboMetricasRelatorioGeral','value'),
                Input('cboAlunos', 'value'),
                Input('cboMetricas', 'value'),
                Input('cboAlunoPolaridade', 'value'),
            ]
        )

        def atualiza_grafico_relatorio_geral(clickData, emotion, aluno_seg_grafico, metrica_seg_grafico, aluno_primeiro_grafico):
            filtraPelaColuna = emotion.lower()
            if filtraPelaColuna != '':
                if filtraPelaColuna in df_relatorio_geral.columns:
                    dff = pd.DataFrame()
                    dff = df_relatorio_geral[df_relatorio_geral[filtraPelaColuna].notnull()]

                    '''contador_indice = 0
                    for i, linha in dff.iterrows():
                        dff.at[i,'indiceUsuario'] = contador_indice
                        contador_indice += 1
                    dff = dff.reset_index()'''
                else:
                    dff = pd.DataFrame()
                    dff[filtraPelaColuna] = None
                    dff['idUsuario'] = None
                    dff['indiceUsuario'] = None

                fig = px.bar(dff, x='indiceUsuario', y=filtraPelaColuna,
                            hover_data=['idUsuario'], color=filtraPelaColuna, labels={'indiceUsuario':'USUÁRIO(S)', 
                            filtraPelaColuna: filtraPelaColuna.upper()}, height=600,
                            color_continuous_scale=['yellow', 'orange',
                                         'deeppink', 'purple',
                                         'blue'])

                if filtraPelaColuna != 'polaridade':
                    fig.update_layout(title_text='Relatório Geral dos Alunos', 
                                xaxis = dict(
                                    tickmode = 'linear',
                                ),
                                title_x=0.5,
                                yaxis_range=[0,1])
                else:
                    valor_minimo = dff[filtraPelaColuna].min() 
                    if float(valor_minimo) < 0:
                        valor_minimo = valor_minimo - 0.1
                    else:
                        valor_minimo = valor_minimo + 0.1

                    valor_maximo = dff[filtraPelaColuna].max() 

                    fig.update_layout(title_text='Relatório Geral dos Alunos', 
                                xaxis = dict(
                                    tickmode = 'linear',
                                ),
                                title_x=0.5,
                                yaxis_range=[valor_minimo, valor_maximo + 0.1])

                if clickData is not None:
                    usuario_procurado = clickData['points'][0]['customdata'][0]
                    clickData = None
                    self.b_clicou_ultimo_grafico = True
                    return fig, usuario_procurado, filtraPelaColuna.upper(), usuario_procurado, None, True

                return fig, aluno_seg_grafico, metrica_seg_grafico, aluno_primeiro_grafico, None, False
            else:
                return '', aluno_seg_grafico, metrica_seg_grafico, aluno_primeiro_grafico, None, False

        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        print('\nPressione CTRL+C para selecionar outra disciplina\n')

        webbrowser.open('http://127.0.0.1:' + str(port))
        app.run(host="127.0.0.1", port=str(port), debug=False)