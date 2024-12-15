import tkinter as tk
from tkinter import ttk
import time
import threading
from widgets.checkboxtable import CheckboxTable
from widgets.settingstab import SettingsTab

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
        
        # Thread de atualização contínua
        self.running = True
        self.update_thread = threading.Thread(target=self.__main_update_loop, daemon=True)
        self.update_thread.start()
        
    def __main_update_loop(self):
        while self.running:
            print('boop')  # Aqui você pode colocar qualquer lógica que deve ser executada continuamente
            print(self.config['properties'])
            time.sleep(5)
            
            
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
    
    # ----------------------------------------------------------------------------------------------------
    # tabs content
    
    def setup_main_tab(self, frame):
        pass
    
    def setup_biomes_tab(self, frame):
        headers = ['Biome', 'Notify', 'Mention', 'Send link', 'Wait duration']
        
        # we will make a checkbox table here
        table = CheckboxTable(frame, title="Preferences", headers=headers, rows=list(self.config['biomes'].keys()), spcx=1, spcy=1, cellbd=0.5, cellrelief=None)
        self.get_checkbox_values = table.get_configurations
            
    def setup_settings_tab(self, frame):
        # frame.config(bg="red")
        settings_tab = SettingsTab(frame, self.config)
    
    def setup_credits_tab(self, frame):
        pass
    
    def setup_debug_tab(self, frame):
        pass
    
        
    # ----------------------------------------------------------------------------------------------------
    # widgets for tabs
    
    def on_close(self):
        self.running = False
        self.root.destroy()
