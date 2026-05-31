# ============================================================
# automacao_wms.py - Automacao de finalizacao de atividades no WMS
# ============================================================
# Este script automatiza ~2000 finalizacoes de atividades no
# sistema WMS (Delphi Desktop) usando pyautogui para cliques
# e pywinauto para conexao com a janela.
#
# Uso:
#   python automacao_wms.py --calibrar   # capturar coordenadas
#   python automacao_wms.py --debug      # listar janelas
#   python automacao_wms.py --teste      # testar 1 atividade
#   python automacao_wms.py --total 500  # rodar N atividades
#
# Para parar: mova o mouse ao CANTO SUPERIOR ESQUERDO
# ============================================================

import pyautogui          # Automacao de mouse e teclado
import time               # Pausas entre acoes
import sys                # Argumentos de linha de comando
import urllib.request     # HTTP para painel web
import urllib.parse       # Codificar parametros HTTP
import json               # (reservado) parse de JSON se necessario
import threading          # Enviar status pro painel em paralelo
from pywinauto import Application  # Conectar a janela do WMS

# ============================================================
# CONFIGURACOES
# ============================================================
# Rode `python automacao_wms.py --calibrar` com o WMS aberto
# na tela de Monitoracao de Atividades (ja filtrada por DEV).
# Depois cole as coordenadas geradas nos comentarios abaixo.

# Lista de titulos de janela do WMS (tenta em ordem ate achar)
JANELAS_WMS = [
    "WMS - Menu Principal",
    "Monitoração geral de atividades",
    "Monitoração de Atividades",
    "Monitoracao geral de atividades",
    "Monitoracao de Atividades",
]

# --- Tela de Monitoracao de Atividades (ja filtrada por DEV) ---
BTN_PRIMEIRA_LINHA   = (392, 128)   # Primeira linha da tabela (duplo clique)

# --- Tela de detalhe da atividade (abre apos duplo clique) ---
BTN_FINALIZAR        = (429, 79)    # Botao "Finalizar Atividade"
BTN_SIM              = (686, 436)   # Popup "Atencao" -> botao "Sim"
BTN_SAIR             = (976, 706)   # Botao "Sair" (fecha detalhe)

# --- Painel Web (opcional) ---
# --- Controles de tempo ---
TEMPO_ESPERA  = 1.5                  # Pausa (seg) entre cada clique
TIMEOUT_TOTAL = 3600                 # Tempo maximo total (1 hora)

# ============================================================
# FUNCOES
# ============================================================

def conectar_wms():
    """
    Tenta conectar a uma janela do WMS percorrenda a lista
    JANELAS_WMS. Retorna (app, janela) ou lanca excecao.
    """
    for titulo in JANELAS_WMS:
        try:
            # Tenta conectar pelo titulo da janela (backend win32)
            app = Application(backend='win32').connect(title=titulo, timeout=3)
            janela = app.window(title=titulo)
            janela.set_focus()               # Traz janela pra frente
            time.sleep(1)
            rect = janela.rectangle()        # Obtem posicao/tamanho
            print(f"Conectado: '{titulo}'")
            print(f"Posicao: ({rect.left}, {rect.top}) - ({rect.right}, {rect.bottom})")
            return app, janela
        except Exception:
            continue                         # Tenta proximo titulo
    raise Exception(f"Nenhuma janela WMS encontrada. Titulos procurados: {JANELAS_WMS}")


def clicar(x, y, duplo=False):
    """
    Clica (ou duplo-clica) na coordenada (x, y) da tela.
    Aguarda TEMPO_ESPERA segundos apos o clique.
    """
    if duplo:
        pyautogui.doubleClick(x, y)
    else:
        pyautogui.click(x, y)
    time.sleep(TEMPO_ESPERA)


def atualizar_painel(feitas, total, status):
    """
    Envia atualizacao de progresso para o painel web PHP
    via HTTP POST. Executado em thread separada para nao travar
    a automacao.
    """
    if not PAINEL_ATIVO:
        return
    try:
        dados = urllib.parse.urlencode({
            "acao": "atualizar_status",
            "feitas": feitas,
            "total": total,
            "status": status
        }).encode()
        urllib.request.urlopen(PAINEL_URL, data=dados, timeout=3)
    except Exception:
        pass  # Falha no painel nao interrompe a automacao


def finalizar_atividade(num):
    """
    Executa o ciclo completo de finalizacao de uma atividade:
    1. Duplo clique na primeira linha da tabela
    2. Clique em "Finalizar Atividade"
    3. Clique em "Sim" (confirmacao)
    4. Clique em "Sair" (volta pra lista)
    """
    print(f"\n=== Atividade #{num} ===")

    print("  Duplo clique na primeira linha...")
    clicar(BTN_PRIMEIRA_LINHA[0], BTN_PRIMEIRA_LINHA[1], duplo=True)

    print("  Clicando Finalizar Atividade...")
    clicar(BTN_FINALIZAR[0], BTN_FINALIZAR[1])

    print("  Confirmando com Sim...")
    clicar(BTN_SIM[0], BTN_SIM[1])

    print("  Clicando Sair...")
    clicar(BTN_SAIR[0], BTN_SAIR[1])

    print(f"  OK - Atividade #{num} finalizada!")


def debug_janelas():
    """
    Lista todas as janelas abertas no Windows com titulo e classe.
    Usado para descobrir o titulo exato da janela do WMS
    quando o script nao consegue conectar.
    """
    print("=" * 60)
    print("   DEBUG - Janelas encontradas")
    print("=" * 60)
    try:
        from pywinauto import Desktop
        wins = Desktop(backend='win32').windows()
        print(f"\nTotal de janelas: {len(wins)}")
        print("\nJanelas com titulo:")
        for w in wins:
            txt = w.window_text()
            if txt:
                print(f"  '{txt}' (class: {w.class_name()})")
    except Exception as e:
        print(f"Erro ao listar janelas: {e}")
    print()


def calibrar():
    """
    Modo de calibracao: o usuario posiciona o mouse sobre cada
    botao e pressiona ENTER. O script captura as coordenadas
    e exibe no formato pronto pra copiar para o topo do arquivo.
    """
    print("=" * 60)
    print("   CALIBRACAO - Automacao WMS")
    print("=" * 60)
    print()
    print("Abra o WMS na tela de Monitoracao de Atividades.")
    print("Deixe o mouse parado 2s sobre cada botao para capturar.")
    print("Pressione ENTER para capturar, ou Ctrl+C para sair.")
    print()
    print("Botoes para calibrar (a lista ja esta filtrada por DEV):")
    print("  1) Primeira linha da tabela")
    print("  2) 'Finalizar Atividade'")
    print("  3) 'Sim' (popup Atencao)")
    print("  4) 'Sair'")
    print()

    import msvcrt

    botoes = [
        "Primeira linha da tabela",
        "'Finalizar Atividade'",
        "'Sim' (popup Atencao)",
        "'Sair'",
    ]

    coords = {}
    for nome in botoes:
        # Aguarda ENTER, depois captura posicao atual do mouse
        input(f"Posicione o mouse sobre {nome} e pressione ENTER...")
        x, y = pyautogui.position()
        coords[nome] = (x, y)
        print(f"  -> Capturado: x={x}, y={y}")
        print()

    print("=" * 60)
    print("COORDENADAS CAPTURADAS:")
    print("=" * 60)
    print(f"BTN_PRIMEIRA_LINHA   = {coords[botoes[0]]}")
    print(f"BTN_FINALIZAR        = {coords[botoes[1]]}")
    print(f"BTN_SIM              = {coords[botoes[2]]}")
    print(f"BTN_SAIR             = {coords[botoes[3]]}")
    print()
    print("Copie esses valores para o topo do arquivo automacao_wms.py")
    print("na secao # CONFIGURACOES")


# ============================================================
# MAIN - Ponto de entrada do script
# ============================================================

if __name__ == "__main__":
    # Ativa fail-safe: mover mouse ao canto superior esquerdo
    # (0,0) interrompe o script imediatamente
    pyautogui.FAILSAFE = True

    # --- Interpreta argumentos da linha de comando ---

    if "--debug" in sys.argv:
        debug_janelas()
        sys.exit(0)

    if "--calibrar" in sys.argv:
        calibrar()
        sys.exit(0)

    if "--teste" in sys.argv:
        total = 1  # Modo teste: apenas 1 atividade
    else:
        try:
            idx = sys.argv.index("--total")
            total = int(sys.argv[idx + 1])
        except (ValueError, IndexError):
            total = 2000  # Padrao: 2000 atividades

    # --- Cabecalho ---
    print("=" * 60)
    print("   AUTOMACAO WMS - Finalizacao de Atividades")
    print(f"   Total: {total} atividades")
    print("=" * 60)
    print()
    print("  PARA PARAR: mova o mouse ao CANTO SUPERIOR ESQUERDO")
    print()
    input("Pressione ENTER para comecar...")
    print()

    # --- Conecta ao WMS ---
    try:
        app, janela = conectar_wms()
    except Exception as e:
        print(f"ERRO: {e}")
        print("Verifique se o WMS esta aberto e logado.")
        sys.exit(1)

    # --- Inicializa variaveis de controle ---
    inicio = time.time()
    sucessos = 0
    erros = 0
    erros_consecutivos = 0

    # Envia status inicial pro painel web (thread separada)
    threading.Thread(target=atualizar_painel, args=(0, total, "rodando"), daemon=True).start()

    # --- Loop principal: finaliza uma atividade por iteracao ---
    for i in range(1, total + 1):
        try:
            # Verifica timeout
            if time.time() - inicio > TIMEOUT_TOTAL:
                print("\n[TIMEOUT] Atingido limite de tempo.")
                break

            finalizar_atividade(i)
            sucessos += 1
            erros_consecutivos = 0

            # Atualiza painel a cada 5 atividades (ou na ultima)
            if i % 5 == 0 or i == total:
                threading.Thread(target=atualizar_painel, args=(i, total, "rodando"), daemon=True).start()

        except pyautogui.FailSafeException:
            # Mouse no canto superior esquerdo -> parada manual
            print(f"\n[PARADA MANUAL] na atividade #{i}")
            threading.Thread(target=atualizar_painel, args=(i, total, "parado"), daemon=True).start()
            break

        except Exception as e:
            # Erro generico (janela fechou, coordenada errada, etc)
            print(f"\n[ERRO] atividade #{i}: {e}")
            erros += 1
            erros_consecutivos += 1
            if erros_consecutivos >= 5:
                print("Muitos erros seguidos. Parando.")
                break
            time.sleep(3)

    # --- Resumo final ---
    duracao = time.time() - inicio
    print("\n" + "=" * 60)
    print("   RESUMO")
    print("=" * 60)
    print(f"  Finalizadas: {sucessos}")
    print(f"  Erros:       {erros}")
    print(f"  Tempo:       {duracao:.0f}s ({duracao/60:.1f}min)")
    if duracao > 0:
        print(f"  Media:       {sucessos/duracao*60:.1f} ativ/min")
    print("=" * 60)
    input("\nPressione ENTER para fechar...")
