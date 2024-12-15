import tkinter as tk
from tkinter import ttk

class SettingsTab:
    def __init__(self, parent_frame, config):
        """
        Initializes the SettingsTab with a configuration dictionary.
        :param config: Dictionary containing configuration properties.
        """
        self.config = config
        self.entry_refs = []  # Store references to text fields for saving later
        self.parent_root =  parent_frame
        
        self.create_tab(parent_frame)

    def _add_setting(self, parent_frame, key, value, parent_config, full_path):
        """
        Adds a label and an entry field for a single setting.
        :param parent_frame: The parent frame to add the widgets.
        :param key: The setting's key.
        :param value: The setting's value.
        :param parent_config: Reference to the parent config dictionary.
        """
        
        print('-------------- ADD SETTING')
        print('Full path: ', full_path)
        print('Key:', key)
        print('Value:', value)
        
        row = parent_frame.grid_size()[1]  # Calculate current row based on grid
        tk.Label(parent_frame, text=key).grid(row=row, column=0, sticky="w", padx=10, pady=1)

        # Create a text field to display and edit the value
        text_var = tk.StringVar(value=value if value is not None else "")
        entry = tk.Entry(parent_frame, textvariable=text_var)
        entry.grid(row=row, column=1, sticky="ew", padx=10, pady=1)

        # Save the text_var and its path to config for later use
        self.entry_refs.append((text_var, parent_config, key, full_path))

        # Allow the entry column to expand horizontally
        parent_frame.columnconfigure(1, weight=1)

    def _iterate_properties(self, properties, parent_config, parent_frame, path=""):
        """
        Recursively iterates over the configuration properties and creates widgets.
        :param properties: Dictionary of properties to iterate over.
        :param parent_config: Reference to the parent config dictionary.
        :param parent_frame: The parent frame to add widgets.
        """
        for key, value in properties.items():
            full_path = f"{path}.{key}" if path else key
            
            if isinstance(value, dict):
                # Create a LabelFrame for nested dictionaries
                group_frame = tk.LabelFrame(parent_frame, text=key, padx=10, pady=10)  # Added bg color for visibility
                group_frame.grid(row=parent_frame.grid_size()[1], column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

                # Configure the parent frame to allow dynamic resizing of rows and columns
                parent_frame.rowconfigure(parent_frame.grid_size()[1] - 1, weight=1)  # Ensure the row of the group_frame can expand

                # Allow the LabelFrame to expand horizontally to take full width of its parent
                parent_frame.columnconfigure(0, weight=1)  # Allow the column to expand (first column where LabelFrame is placed)
                group_frame.grid_columnconfigure(0, weight=1)  # Allow LabelFrame to expand in its internal columns

                # Recursively add settings inside the group_frame (LabelFrame)
                self._iterate_properties(value, parent_config[key], group_frame, full_path)
            else:
                self._add_setting(parent_frame, key, value, parent_config, full_path)
                
              
    # send a new config file for us to re-create everything in the same root
    def update(self, new_config):
        self.config = new_config
        self.create_tab(self.parent_root) # regenerate everything?
        
    def create_tab(self, parent_frame):
        """
        Creates the settings tab in the provided parent frame with scroll support.
        :param parent_frame: The frame where the tab should be created.
        """
        # Create a canvas and a frame for the scrollable area
        canvas = tk.Canvas(parent_frame)  # Save canvas reference here
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # Configure the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add the scrollable area to the parent frame using grid()
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(0, weight=1)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="motherfucker")

        # Update the scroll region when the content changes
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Criação de um "path" que guarda o caminho completo para cada valor
        self.entry_refs = []

        def _iterate_properties(config, parent_config, parent_frame, path=""):
            """
            Função para iterar sobre a configuração, criando os campos de entrada e armazenando os caminhos.
            :param config: O dicionário de configurações
            :param parent_config: O dicionário pai
            :param parent_frame: O frame onde os widgets serão adicionados
            :param path: O caminho atual da chave no dicionário
            """
            for key, value in config.items():
                full_path = f"{path}.{key}" if path else key

                if isinstance(value, dict):
                    # Criar um LabelFrame para o dicionário
                    frame = tk.LabelFrame(parent_frame, text=key, padx=10, pady=10)
                    frame.grid(sticky="nsew", padx=10, pady=10)
                    parent_frame.grid_rowconfigure(frame, weight=1)
                    parent_frame.grid_columnconfigure(frame, weight=1)
                    _iterate_properties(value, parent_config, frame, full_path)
                elif isinstance(value, list):
                    # Para cada item da lista, criar um campo de entrada
                    for i, item in enumerate(value):
                        _iterate_properties(item, parent_config, parent_frame, f"{full_path}[{i}]")
                else:
                    # Criar os campos de entrada para valores simples (string, int, bool, etc)
                    var = tk.StringVar(value=value)
                    entry = tk.Entry(parent_frame, textvariable=var)
                    entry.grid(sticky="nsew", padx=10, pady=5)
                    
                    # Guardar o caminho completo e o campo de entrada
                    self.entry_refs.append((var, parent_config, full_path))

        # Iterar e criar os widgets de configuração
        self._iterate_properties(self.config, self.config, scrollable_frame)

        def save_changes():
            """
            Saves all changes from text fields back to the config.
            """

            print('saving changes...')

            # Vamos criar um novo dicionário para armazenar o dicionário reconstruído
            reconstructed_dict = self.config.copy()  # Copia o dicionário original para preservar o original

            for text_var, parent_config, key, path in self.entry_refs:

                # Divida o path em partes e percorra os níveis do dicionário
                keys = path.split('.')

                # Comece com a cópia do dicionário original
                config_to_update = reconstructed_dict

                for key in keys[:-1]:  # Para todos os níveis, exceto o último
                    # Navegue até o próximo nível, criando o dicionário se não existir
                    if key not in config_to_update:
                        config_to_update[key] = {}
                    config_to_update = config_to_update[key]

                # Última chave onde o valor será atualizado
                last_key = keys[-1]

                # Atualize o valor no dicionário reconstruído
                config_to_update[last_key] = text_var.get() or None  # Atualize com o valor inserido (ou None se vazio)

            # Aqui você apenas imprime o dicionário reconstruído
            self.config = reconstructed_dict


        # Add a "Save" button at the bottom of the scrollable frame
        save_button = tk.Button(parent_frame, text="Save", command=save_changes)
        save_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Ensure canvas resizes with the frame and adjusts the width of the inner frame
        def FrameWidth(event):
            canvas_width = event.width
            canvas.itemconfig(canvas.find_withtag("motherfucker"), width=canvas_width)
            # This will ensure the scroll region gets updated after the canvas size changes
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def _on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # Bind the canvas to handle its resizing correctly
        canvas.bind("<Configure>", FrameWidth)

        # Make canvas scroll delta functionality for mouse wheel (Capture anywhere in the canvas)
        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
