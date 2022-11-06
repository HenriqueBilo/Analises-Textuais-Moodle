#from pickle import FALSE

from MoodleApi import *
from Usuarios import *
from Cursos import *
from Foruns import *
from Discussoes import *
from Postagens import *
from Chats import *
from Autenticacao import *
from LeituraCsvs import *
from FuncoesAuxiliares import *
from AnalisesResultados import *
from GraficosMetricas import *

if __name__ == '__main__':

    funcoes_auxiliares = FuncoesAuxiliares()

    # Pega informações do usuário
    lista_cursos_usuario, id_usuario_buscado = funcoes_auxiliares.pega_informacoes_usuario()

    # Seleciona o curso
    id_disciplina_escolhida = funcoes_auxiliares.menu_selecao_curso(lista_cursos_usuario)

    print('\n ------ Processando... Aguarde um momento ------')

    # Pega as mensagens dos chats do curso
    cursos_array = funcoes_auxiliares.coleta_mensagens_chat_do_curso(id_disciplina_escolhida)

    # Pega as direct messages
    funcoes_auxiliares.coleta_mensagens_diretas_ao_professor(cursos_array, id_usuario_buscado)

    # Pega as mensagens dos fóruns
    funcoes_auxiliares.coleta_mensagens_dos_foruns(cursos_array)

    leitura_arquivos = LeituraCsvs()

    retornoMensagensChats = leitura_arquivos.get_dados_chats_mensagens()
    retornoMensagensDiretas = leitura_arquivos.get_dados_mensagens_diretas()
    retornoMensagensPostsForuns = leitura_arquivos.get_dados_posts()

    #Preparação Dados para análise
    funcoes_auxiliares.grava_csv_unico(retornoMensagensChats.loc[:].values, retornoMensagensDiretas.loc[:].values, retornoMensagensPostsForuns.loc[:].values)

    retornoMensagens = pd.read_csv('./data/dados_mensagens.csv', sep='-')

    analises_resultados = AnalisesResultados()
    analises_resultados.analise_metricas(retornoMensagens.loc[:].values)
    
    graficos_resultados = GraficosMetricas()
    graficos_resultados.cria_grafico_metricas()

