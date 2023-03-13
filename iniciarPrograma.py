from src.MoodleApi import *
from src.Usuarios import *
from src.Cursos import *
from src.Foruns import *
from src.Discussoes import *
from src.Postagens import *
from src.Chats import *
from src.Autenticacao import *
from src.LeituraCsvs import *
from src.FuncoesAuxiliares import *
from src.AnalisesResultados import *
from src.GraficosMetricas import *

if __name__ == '__main__':
    if not os.path.isdir('./data'):
        os.makedirs('./data')

    id_disciplina_escolhida = ''

    port = 8050

    while id_disciplina_escolhida != 0:
        funcoes_auxiliares = FuncoesAuxiliares()

        # Pega informações do usuário
        lista_cursos_usuario, id_usuario_buscado = funcoes_auxiliares.pega_informacoes_usuario()

        # Seleciona o curso
        id_disciplina_escolhida = funcoes_auxiliares.menu_selecao_curso(lista_cursos_usuario)

        if id_disciplina_escolhida == '0':
            break

        print('\n ------ Processando... Aguarde um momento ------')

        # Pega as mensagens dos chats do curso
        cursos_array = funcoes_auxiliares.coleta_mensagens_chat_do_curso(id_disciplina_escolhida)

        # Pega as direct messages
        funcoes_auxiliares.coleta_mensagens_diretas_ao_professor(cursos_array, id_usuario_buscado)

        # Pega as mensagens dos fóruns
        dados_usuarios = pd.read_csv('./data/dados_usuarios.csv', sep='-')
        funcoes_auxiliares.coleta_mensagens_dos_foruns(cursos_array, dados_usuarios.loc[:].values)

        leitura_arquivos = LeituraCsvs()

        retornoMensagensChats = leitura_arquivos.get_dados_chats_mensagens()
        retornoMensagensDiretas = leitura_arquivos.get_dados_mensagens_diretas()
        retornoMensagensPostsForuns = leitura_arquivos.get_dados_posts()

        #Preparação Dados para análise
        funcoes_auxiliares.grava_csv_unico(retornoMensagensChats.loc[:].values, retornoMensagensDiretas.loc[:].values, retornoMensagensPostsForuns.loc[:].values)

        retornoMensagens = pd.read_csv('./data/dados_mensagens.csv', sep='-')

        analises_resultados = AnalisesResultados()
        analises_resultados.analise_metricas(retornoMensagens.loc[:].values)

        port += 1
        graficos_resultados = GraficosMetricas()
        graficos_resultados.prepara_dados_gerais_graficos(port)

        funcoes_auxiliares = FuncoesAuxiliares()
        funcoes_auxiliares.deleta_arquivos_auxiliares()
