import tkinter as tk
from tkinter import ttk
import time
import threading
from widgets.checkboxtable import CheckboxTable
from widgets.settingstab import SettingsTab
import webbrowser # to make credit links clickable lol
import os

# to generate configuration string
import pickle
import base64

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Sol's RNG Biome Grinder")
        self.root.geometry("800x600")
        self.root.minsize(400, 300)
        
        self.config = {
            'biomes': {
                
                'Glitched': {
                    'category': 'biome',
                    'color': '#bfff00',
                    'chance': 30000,
                    'duration': 164
                },

                'Null': {
                    'category': 'biome',
                    'color': '#838383',
                    'chance': 13333,
                    'duration': 99
                },

                'Corruption': {
                    'category': 'biome',
                    'color': '#6d32a8',
                    'chance': 9000,
                    'duration': 660
                },

                'Starfall': {
                    'category': 'biome',
                    'color': '#011ab7',
                    'chance': 7500,
                    'duration': 600
                },

                'Hell': {
                    'category': 'biome',
                    'color': '#ff4719',
                    'chance': 6666,
                    'duration': 660
                },

                'SandStorm': {
                    'category': 'biome',
                    'color': '#ffc600',
                    'chance': 3000,
                    'duration': 600
                },

                'Rainy': {
                    'category': 'weather',
                    'color': '#027cbd',
                    'chance': 750,
                    'duration': 120
                },

                'Snowy': {
                    'category': 'weather',
                    'color': '#dceff9',
                    'chance': 600,
                    'duration': 120
                },

                'Windy': {
                    'category': 'weather',
                    'color': '#9ae5ff',
                    'chance': 500,
                    'duration': 120
                },

                'Normal': {
                    'category': 'biome',
                    'color': '#ffffff',
                    'chance': 0,
                    'duration': 0
                },
                
                # TODO(adrian): make a way to wait until biome change, instead of set timers
                # since this biome is not "straight-timer-related"
                # >>> 'duration': 'ON_CHANGE'
                'Pumpkin Moon': {
                    'category': 'event_biome',
                    'color': '#f7b429',
                    'chance': 'unk',
                    'duration': 180,
                },
                
                # TODO(adrian): make a way to wait until biome change, instead of set timers
                # since this biome is not "straight-timer-related"
                # >>> 'duration': 'ON_CHANGE'
                'Grave yard': {
                    'category': 'event_biome',
                    'color': '#bdbdbd',
                    'chance': 'unk',
                    'duration': 180,
                },
                
                'Unknown': {
                    'category': 'biome',
                    'color': '#000000',
                    'chance': 0,
                    'duration': 0
                }
                
            },
            
            'properties': {
                'ROBLOX': {
                    'PRIVATE_SERVER_URL': None,
                },
                'DISCORD': {
                    'WEBHOOK_URL': None,
                    'MENTIONS': None,
                },
                'INTERNAL': {
                    'TEST_ONE': None,
                    'TEST_TWO': None,
                    'TEST_THREE': None,
                    'TESTING': {
                        'POTATO': '1',
                        'BATATA': 1
                    }
                }
            }
            
        }
        
        # Criação da interface
        self.setup_ui()
        
        # GUI is ready to be used // load values etc...
        self.on_gui_ready()
        
        # Thread de atualização contínua
        self.running = True
        self.update_thread = threading.Thread(target=self.__main_update_loop, daemon=True)
        self.update_thread.start()
        
    # ----------------------------------------------------------------------------------------------------
    # 
    
    def __main_update_loop(self):
        while self.running:
            print('boop')  # Aqui você pode colocar qualquer lógica que deve ser executada continuamente
            print(self.config['properties'])
            time.sleep(5)
            
    # ----------------------------------------------------------------------------------------------------
    # util funcs
    
    def get_config(self):
        """
        Gera uma string "non-sense" representando as configurações.
        :param config: O objeto de configuração (self.config).
        :return: Uma string codificada que representa a configuração.
        """
        # Serializa o objeto de configuração para bytes
        self.config['BIOME_CHECKBOX'] = self.biome_checkbox_table.get_values()
        
        serialized_config = pickle.dumps(self.config)
        
        # Codifica os bytes para uma string base64
        encoded_config = base64.urlsafe_b64encode(serialized_config).decode('utf-8')
        
        # Retorna a string base64 "non-sense" compacta
        return encoded_config
    
    def load_config(self, serialized_config):
        """
        Carrega a configuração de volta a partir de uma string "non-sense".
        :param serialized_config: A string gerada por get_config.
        :return: O objeto de configuração restaurado.
        """
        
        if not serialized_config: 
            print('>> No config key to load!')
            return
        
        try:
            # Primeiro, decodifica a string base64 de volta para os bytes originais
            decoded_config = base64.urlsafe_b64decode(serialized_config)
            
            # Agora, desserializa os bytes para o objeto original
            config = pickle.loads(decoded_config)

            # extract biome checkboxes            
            BIOME_CONFIG = config['BIOME_CHECKBOX']
            config.pop('BIOME_CHECKBOX') # remove so this doesnt mess up the rest of the config
            self.biome_checkbox_table.set_values(BIOME_CONFIG) # use the retrieved checkboxes to update ours
            self.settings_tab.update(config)
            self.config = config
            
            # Retorna a configuração restaurada
            return config
        except Exception as e:
            print(f"Erro ao carregar a configuração: {e}")
            return None
        
    # ----------------------------------------------------------------------------------------------------
    # "generators"
    
    def add_tab(self, notebook, tab_name, setup_function):
        """
        Creates a new tab in notebook
        @NOTE: This will send the generated tab frame as argument for setup_function. It is 
        expected that setup_function is from this class, because it will call with (self, tab_frame)
        """
        
        tab_frame = tk.Frame(notebook)
        notebook.add(tab_frame,text=tab_name)
        setup_function(tab_frame)
    
    # ----------------------------------------------------------------------------------------------------
    # main application setup
    
    def setup_ui(self):
        
        # Criação do Notebook para as abas (guia)
        notebook = ttk.Notebook(self.root)
        notebook.pack(padx=10, fill="both", expand=True)
        
        self.add_tab(notebook, "Main", self.setup_main_tab)
        self.add_tab(notebook, "Biomes", self.setup_biomes_tab)
        self.add_tab(notebook, "Settings", self.setup_settings_tab)
        self.add_tab(notebook, "Credits", self.setup_credits_tab)
        
        notebook.select(None) # fuck off
        
        footer = tk.Frame(self.root)
        footer.pack(side="bottom", fill="x", padx=10, pady=5)
        
        # Criar o botão START (F1)
        start_button = tk.Button(footer, text="F1 - START", command=self.start_button)
        start_button.pack(side="left", padx=5)

        # Criar o botão STOP (F3)
        stop_button = tk.Button(footer, text="F3 - STOP", command=self.stop_button)
        stop_button.pack(side="left", padx=5)
        
        # Espaço para os botões Import e Export
        footer_right = tk.Frame(footer)
        footer_right.pack(side="right")

        # Botão e campo de entrada para Import
        import_entry = tk.Entry(footer_right, width=15)
        import_entry.pack(side="left", padx=5)
        
        def on_import_click():
            """
            Pega o conteúdo do Entry Import e passa para self.load_config().
            """
            content = import_entry.get()
            if content:  # Verifica se tem algo para importar
                self.load_config(content)
        
        import_button = tk.Button(footer_right, text="Import", command=on_import_click)
        import_button.pack(side="left", padx=5)
        
        # Botão e campo de entrada para Export (somente leitura)
        export_var = tk.StringVar()  # StringVar para controlar o conteúdo do Entry
        export_entry = tk.Entry(footer_right, textvariable=export_var, width=15, state="readonly")
        export_entry.pack(side="left", padx=5)
        
        def on_export_click():
            """
            Chama self.get_config() e coloca o resultado no Entry Export.
            """
            result = self.get_config()
            export_entry.config(state="normal")  # Torna o entry editável temporariamente
            export_var.set(result)  # Define o valor no entry
            export_entry.config(state="readonly")  # Retorna para somente leitura

        export_button = tk.Button(footer_right, text="Export", command=on_export_click)
        export_button.pack(side="left", padx=5)
        
    def start_button(self):
        print('start pressed')
        
    def stop_button(self):
        print('stop pressed')
        
    def on_gui_ready(self):
        print('GUI Starting...')
        
        try:
            print('Trying to load configuration...')
            with open(os.path.join(os.path.dirname(__file__), 'configkey.txt'), 'r') as f:
                self.load_config(f.read().strip())
        except Exception as e:
            print(f'Error while loading config: {e}')
        
    def on_gui_close(self):
        print('GUI Closing...')
        self.running = False
        self.root.destroy()
        
        print('-------------------------- COMPACTING --------------------------')
        print(self.config)
        serialized_config = self.get_config()
        print('Serialized: ', serialized_config)
        # store the serialized key into configkey.txt
        with open(os.path.join(os.path.dirname(__file__), 'configkey.txt'), 'w') as f:
            f.write(serialized_config)
        print('KEY WRITTEN!')
        
        # save application config somewhere to read back later
    
    # ----------------------------------------------------------------------------------------------------
    # tabs content
    
    def setup_main_tab(self, frame):
        pass
    
    def setup_biomes_tab(self, frame):
        headers = ['Biome', 'Notify', 'Mention', 'Send link', 'Wait duration']
        
        # we will make a checkbox table here
        table = CheckboxTable(frame, title="Preferences", headers=headers, rows=list(self.config['biomes'].keys()), spcx=1, spcy=1, cellbd=0.5, cellrelief=None)
        self.biome_checkbox_table = table
            
    def setup_settings_tab(self, frame):
        # frame.config(bg="red")
        settings_tab = SettingsTab(frame, self.config)
        self.settings_tab = settings_tab
    
    def setup_credits_tab(self, frame):
        """
        Sets up the 'Credits' tab with the desired text.
        :param frame: The parent frame where the tab content will be added.
        """
        
        # # Criar um Text widget para mostrar o texto
        credits_text = "made with <3 by @masutty\n\nspecial thanks:\n@evcskies - sharing, support, community"
        
        text_widget = tk.Text(frame, wrap="word", font=("Arial", 12), height=4, bd=0, bg=frame.cget('bg'))
        text_widget.insert("1.0", credits_text)
        text_widget.pack()
        text_widget.place(relx=0.5, rely=0.5, anchor="center")

        # # Agora, vamos colorir o <3> em vermelho
        text_widget.tag_configure("red", foreground="red")
        text_widget.tag_configure("center", justify='center')
        text_widget.tag_add("red", "1.10", "1.13")  # Marca o <3> para colorir
        text_widget.tag_add("center", "1.0", "end")  # Marca o texto para alinhar ao centro
        
        # Tornar @masutty clicável
        text_widget.tag_add("masutty", "1.16", "1.end")
        text_widget.tag_configure("masutty", foreground="blue")
        text_widget.tag_bind("masutty", "<Button-1>", lambda e: open_link("https://github.com/adriankubinyete"))
        
        # Tornar @evcskies clicável
        text_widget.tag_add("evcskies", "4.0", "4.9")
        text_widget.tag_configure("evcskies", foreground="blue")
        text_widget.tag_bind("evcskies", "<Button-1>", lambda e: open_link("https://www.youtube.com/@evcskies"))
        
        def open_link(url):
            webbrowser.open(url)
    
    def setup_debug_tab(self, frame):
        pass
    
        
    # ----------------------------------------------------------------------------------------------------
    # widgets for tabs
    
    
