import tkinter as tk

class CheckboxTable:
    def __init__(self, parent_frame, title, headers, rows, spcx=1, spcy=1, cellbd=0.5, cellrelief="solid"):
        self.title = title
        self.parent_frame = parent_frame
        self.headers = headers  # Cabeçalhos das colunas
        self.rows = rows        # Linhas de dados
        self.column_spacing = spcx  # Espaçamento horizontal
        self.row_spacing = spcy    # Espaçamento vertical
        self.cell_border = cellbd  # Borda das células
        self.cell_relief = cellrelief  # Estilo da borda das células

        # Armazenar as variáveis dos checkboxes para acesso futuro
        self.check_vars = []

        # Criar o frame para a tabela (não mais um LabelFrame)
        self.table_frame = tk.Frame(self.parent_frame)
        self.table_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Tornar o parent_frame e o table_frame redimensionáveis
        self.parent_frame.grid_rowconfigure(0, weight=1)  # O frame do parent pode crescer na linha 0
        self.parent_frame.grid_columnconfigure(0, weight=1)  # O frame do parent pode crescer na coluna 0

        # Tornar o table_frame redimensionável para preencher o espaço
        self.table_frame.grid_rowconfigure(0, weight=0)  # Linha do cabeçalho não vai expandir
        for i in range(len(self.rows) + 1):  # Para cada linha da tabela, exceto o cabeçalho
            self.table_frame.grid_rowconfigure(i + 1, weight=1)  # As linhas podem expandir

        # Criar cabeçalhos
        for col, header in enumerate(self.headers):
            label = tk.Label(self.table_frame, text=header, anchor="center", font=("Arial", 10, "bold"),
                             bg="#d5efff", bd=self.cell_border, relief=self.cell_relief)
            label.grid(row=0, column=col, padx=self.column_spacing, pady=self.row_spacing, sticky="nsew")

            # Ajustar as colunas para ficarem redimensionáveis
            self.table_frame.grid_columnconfigure(col, weight=1, uniform="column")

        # Criar as linhas da tabela
        for row_index, row_name in enumerate(self.rows):
            self.add_row(row_index + 1, row_name)

    def add_row(self, row_index, row_name):
        row_color = "#e2e8ec" if row_index % 2 == 0 else "#ffffff"

        # Criar uma nova linha com o nome da configuração
        tk.Label(self.table_frame, text=row_name, anchor="center", bg=row_color, bd=self.cell_border,
                 relief=self.cell_relief).grid(
            row=row_index, column=0, padx=self.column_spacing, pady=self.row_spacing, sticky="nsew")

        # Adicionar os checkbuttons para cada coluna
        checkbuttons = []
        for col in range(1, len(self.headers)):
            var = tk.BooleanVar(value=False)
            
            # Checkbutton estilizado
            cb = tk.Checkbutton(self.table_frame, variable=var, bg="#ffbaba", selectcolor="#c0e0c0",
                                indicatoron=False,  # Usando a forma "simples" sem a caixa de seleção padrão
                                relief="flat", bd=0, highlightthickness=0,
                                activebackground="#a0c0e0", activeforeground="#a0c0e0")
            cb.grid(row=row_index, column=col, padx=self.column_spacing, pady=self.row_spacing, sticky="nsew")
            checkbuttons.append(var)

        # Armazenar as variáveis de cada linha (para acesso futuro)
        self.check_vars.append(checkbuttons)

    def get_configurations(self):
        """
        Retorna os valores de todos os checkboxes em formato de lista de listas.
        Cada lista interna contém os valores (True/False) dos checkboxes para uma linha.
        """
        return [[var.get() for var in row] for row in self.check_vars]
