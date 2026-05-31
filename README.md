# automacao-wms

Automação de finalização de atividades no sistema WMS (Delphi Desktop) usando Python.

## O problema

O WMS não tem opção de "selecionar tudo" ou "finalizar em lote". Cada atividade precisa ser finalizada individualmente: clicar na linha → Finalizar Atividade → Sim → Sair. Para 2000 atividades, são ~8000 cliques manuais.

## Como usar

```bash
pip install -r requirements.txt

# 1. Descobrir o titulo exato da janela do WMS
python automacao_wms.py --debug

# 2. Calibrar as coordenadas dos botoes
python automacao_wms.py --calibrar

# 3. Testar com 1 atividade
python automacao_wms.py --teste

# 4. Rodar em massa
python automacao_wms.py --total 2000
```

Para **parar** a qualquer momento: mova o mouse para o **canto superior esquerdo** da tela.

## Quer automatizar outra coisa?

O padrão é simples:

```python
import pyautogui
import time

# Clicar
pyautogui.click(x, y)
pyautogui.doubleClick(x, y)

# Mover
pyautogui.moveTo(x, y, duration=1)

# Digitar
pyautogui.write("texto")

# Tecla especial
pyautogui.press("enter")

# Capturar posicao do mouse
x, y = pyautogui.position()

# Para parar o script
pyautogui.FAILSAFE = True  # mouse no canto (0,0) interrompe
```

Dicas para criar seu próprio script:

| Situação | Como resolver |
|----------|--------------|
| Software web | Use `pyautogui` + `selenium` (mais confiável que coordenadas) |
| Software desktop Windows | Use `pywinauto` para achar a janela, `pyautogui` para clicar |
| Botão muda de posição | Use `pyautogui.locateOnScreen('botao.png')` (precisa da imagem) |
| Precisa esperar algo carregar | `time.sleep(segundos)` ou loop até achar a janela |

## Requisitos

- Python 3.8+
- Windows (para pywinauto)
- pip install pyautogui pywinauto
