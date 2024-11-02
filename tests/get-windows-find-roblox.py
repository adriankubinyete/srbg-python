import pygetwindow as gw
import psutil

def get_roblox_data():
    """Verifica se o Roblox está aberto e retorna a janela do Roblox."""
    roblox_windows = gw.getWindowsWithTitle('Roblox')  # Pega todas as janelas com título 'Roblox'
    window_count = len(roblox_windows)

    if window_count == 0:
        return None  # Roblox não está aberto
    elif window_count > 1:
        print(f"Encontradas {window_count} janelas do Roblox.")

    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'] == 'RobloxPlayerBeta.exe':  # Nome correto do processo
            roblox_window = roblox_windows[0]  # Pega a primeira janela do Roblox
            data = {
                'process': proc.info['pid'],
                'window': roblox_window
            }
            return data
    return None

# Uso
roblox_data = get_roblox_data()
if roblox_data:
    print("Roblox está aberto.")
    print(f"Dados do Roblox: {roblox_data}")
else:
    print("Roblox não está aberto.")
