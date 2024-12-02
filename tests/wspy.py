import tkinter as tk
from tkinter import ttk
import win32process
import pygetwindow as gw
import pyautogui
import psutil
import threading
import time

class WindowSpy:
    def __init__(self, root):
        self.root = root
        self.root.title("Window Info Reader")
        self.root.geometry("600x700")
        self.root.minsize(500, 500)
        
        self.counter=0
        
        # Variáveis
        self.selected_window = None
        self.follow_mouse = tk.BooleanVar()
        self.tooltip_toggle = tk.BooleanVar()
        self.tooltips = {}
        
        self.config = {
            "WINDOW_CLIENT_X_OFFSET": 8,
            "WINDOW_CLIENT_Y_OFFSET": 31,
            "MAIN_UPDATE_LOOP_INTERVAL_MS": 100,
        }

        # Widgets
        self.setup_ui()

        # Thread para atualização contínua
        self.running = True
        self.update_thread = threading.Thread(target=self.main_update_loop, daemon=True)
        self.update_thread.start()

    def setup_ui(self):
        monospace_font = ("Courier", 10)
        
        # Seção de sistema
        section_system = tk.LabelFrame(self.root, text="System Information", padx=10, pady=10)
        section_system.pack(fill="x", padx=10, pady=5)

        self.system_info_label = tk.Label(section_system, text="Loading system info...", anchor="w", justify="left")
        self.system_info_label.config(font=monospace_font)
        self.system_info_label.pack(fill="both")

        # Seção de aplicação
        section1 = tk.LabelFrame(self.root, text="Application", padx=10, pady=10)
        section1.pack(fill="x", padx=10, pady=5)

        frame_app = tk.Frame(section1)
        frame_app.pack(fill="x")

        self.window_list = ttk.Combobox(frame_app, state="readonly", width=30)
        self.window_list.pack(side="left", padx=5, fill="x")
        self.update_window_list()
        self.window_list.bind("<<ComboboxSelected>>", self.select_window)

        self.follow_mouse_cb = tk.Checkbutton(frame_app, text="Follow Mouse", variable=self.follow_mouse)
        self.follow_mouse_cb.pack(side="right", padx=5)

        # Checkbox para mostrar tooltip (agora na seção de aplicação)
        self.tooltip_cb = tk.Checkbutton(
            frame_app, text="Show Tooltip", variable=self.tooltip_toggle, command=self.update_tooltip_visibility
        )
        self.tooltip_cb.pack(side="right", padx=5)

        # Seção de processo
        self.section_process = self.create_scrollable_section("Process", height=5)
        self.process_info_label = tk.Label(self.section_process.inner_frame, text="No process selected", justify="left", anchor="w")
        self.process_info_label.config(font=monospace_font)
        self.process_info_label.pack(fill="both", padx=5, pady=5)

        # Seção de janela
        self.section_window = self.create_scrollable_section("Window", height=5)
        self.window_info_label = tk.Label(self.section_window.inner_frame, text="No window selected", justify="left", anchor="w")
        self.window_info_label.config(font=monospace_font)
        self.window_info_label.pack(fill="both", padx=5, pady=5)

        # Seção de informações do mouse
        self.section_mouse = self.create_scrollable_section("Mouse Information", height=5)
        self.mouse_info_label = tk.Label(self.section_mouse.inner_frame, text="Mouse information will appear here", justify="left", anchor="w")
        self.mouse_info_label.config(font=monospace_font)
        self.mouse_info_label.pack(fill="both", padx=5, pady=5)
            
    def create_tooltip(self, name, x, y, title=""):
        """Cria uma tooltip e a armazena em self.tooltips."""
    
        # Cria a nova janela de tooltip
        tooltip_window = tk.Toplevel(self.root)
        tooltip_window.geometry(f"5x5+{x}+{y}")  # Tamanho inicial de 5x5 e a posição (x, y)
        tooltip_window.overrideredirect(True)  # Remove bordas e barra de título
        tooltip_window.config(bg="white", bd=1, relief="solid")
        
        tooltip_window.attributes('-topmost', True)  # Mantém a tooltip acima de outras janelas
        
        tooltip_window.withdraw()  # Mantém a tooltip oculta até ser ativada pelo 'show tooltips'
        
        # Cria a label dentro da tooltip
        label = tk.Label(tooltip_window, text=title, bg="white", anchor="center", justify="center")
        label.pack(padx=0, pady=0)  # Adiciona algum espaço interno (padding) ao redor do texto

        # Atualiza a largura e altura da tooltip imediatamente
        label_width = label.winfo_width()  # Pega a largura da label
        label_height = label.winfo_height()  # Pega a altura da label
        tooltip_window.geometry(f"{label_width+10}x{label_height+10}+{x}+{y}")  # Ajusta a geometria da tooltip, com algum espaço adicional
        
        # Adiciona a tooltip ao dicionário com nome, título e coordenadas
        self.tooltips[name] = {
            'title': title,
            'x': x,
            'y': y,
            'window': tooltip_window,  # Guardamos também a referência para a janela
            'label': label  # Guarda a referência à label para atualizar depois
        }

    def create_scrollable_section(self, title, height):
        frame = tk.LabelFrame(self.root, text=title, padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        canvas = tk.Canvas(frame, height=height * 20)
        scroll_x = ttk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
        scroll_y = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # Vincula a configuração do canvas para atualizar o scrollregion
        scrollable_frame.bind(
            "<Configure>", lambda e: self.on_configure_canvas(e, canvas, scroll_x)
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        # Vincula o scroll do mouse ao canvas
        canvas.bind("<Enter>", lambda e: self.bind_mouse_scroll(canvas))
        canvas.bind("<Leave>", lambda e: self.unbind_mouse_scroll(canvas))

        # Pack do canvas: usa fill="both" para preencher o espaço disponível
        canvas.pack(side="left", fill="both", expand=True)

        # Pack do scroll_x: deve ocupar toda a largura disponível
        scroll_x.pack(side="bottom", fill="x")

        # Pack do scroll_y: deve ocupar a altura da tela, à direita
        scroll_y.pack(side="right", fill="y")

        frame.canvas = canvas
        frame.inner_frame = scrollable_frame

        return frame

    def select_window(self, event):
        selected_title = self.window_list.get()
        windows = gw.getAllWindows()
        for window in windows:
            if window.title == selected_title:
                self.selected_window = window
                break
        
    # ==================================================================================================== #
    # Updating data
    
    def update_window_list(self):
        windows = gw.getAllTitles()
        windows = [w for w in windows if w.strip()]
        self.window_list["values"] = windows

    def update_label(self, label, text):
        """Atualiza o texto da label da tooltip."""
        if label:  # Verifica se a label existe antes de tentar configurar o texto
            label.config(text=text)
                    
    def destroy_tooltip(self):
        """Destrói a tooltip caso ela esteja visível."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None  # Limpa a referência para garantir que a tooltip seja recriada na próxima vez

    def main_update_loop(self):
        while self.running:
            self.update_section_info_system()
            self.update_section_info_process()
            self.update_section_info_window()
            self.update_section_info_mouse()
            self.update_tooltip_visibility()
            time.sleep(self.config.get("MAIN_UPDATE_LOOP_INTERVAL_MS", 1000) / 1000)
            
    def update_section_info_system(self):
        system_info = f"Screen Size: {pyautogui.size().width} x {pyautogui.size().height}"
        self.update_label(self.system_info_label, system_info)

    def update_section_info_process(self):
        if self.selected_window:
            try:
                _, pid = win32process.GetWindowThreadProcessId(self.selected_window._hWnd)
                process = psutil.Process(pid)
                process_info = (
                    f"Process ID: {process.pid}\n"
                    f"Executable: {process.name()}\n"
                    f"Path: {process.exe()}\n"
                )
            except Exception as e:
                process_info = f"Process Info Unavailable: {e}"

            self.update_label(self.process_info_label, process_info)

    def update_section_info_window(self):
        if self.selected_window:
            CLIENT_X_OFFSET = self.config.get('CLIENT_X_OFFSET', 8)
            CLIENT_Y_OFFSET = self.config.get('CLIENT_Y_OFFSET', 31)

            window_info = (
                f"Title:      {self.selected_window.title}\n"
                f"Size:       {self.selected_window.width} x {self.selected_window.height}\n"
                f"Position:   {self.selected_window.left}, {self.selected_window.top}\n"
                f"Minimized:  {self.selected_window.isMinimized}, Maximized: {self.selected_window.isMaximized}, onFocus: {self.selected_window.isActive}\n"
                f"Window:     x: {self.selected_window.left:<4} y: {self.selected_window.top:<4} w: {self.selected_window.width:<4} h: {self.selected_window.height:<4}\n"
                f"Client:     x: {self.selected_window.left + CLIENT_X_OFFSET:<4} y: {self.selected_window.top + CLIENT_Y_OFFSET:<4} w: {self.selected_window.width - 2 * CLIENT_X_OFFSET:<4} h: {self.selected_window.height - 2 * CLIENT_Y_OFFSET:<4}\n"
            )
            self.update_label(self.window_info_label, window_info)

    def update_section_info_mouse(self):
        
        if self.follow_mouse.get():
            CLIENT_X_OFFSET = self.config.get('CLIENT_X_OFFSET', 8)
            CLIENT_Y_OFFSET = self.config.get('CLIENT_Y_OFFSET', 31)
            mouse_x, mouse_y = pyautogui.position()

            screen_info = f'x: {mouse_x:<4} y: {mouse_y:<4}'

            if self.selected_window and not self.selected_window.isMinimized:
                # window and invisible margin (not recommended)
                window_w = self.selected_window.width if self.selected_window else 0
                window_h = self.selected_window.height if self.selected_window else 0
                window_x = mouse_x - self.selected_window.left if self.selected_window else 0
                window_y = mouse_y - self.selected_window.top if self.selected_window else 0
                window_info = f"x: {window_x:<4} y: {window_y:<4} w: {window_w:<4} h: {window_h:<4}"

                # game screen only
                client_w = window_w - 2 * CLIENT_X_OFFSET
                client_h = window_h - 2 * CLIENT_Y_OFFSET
                client_x = mouse_x - (self.selected_window.left + CLIENT_X_OFFSET) if self.selected_window else 0
                client_y = mouse_y - (self.selected_window.top + CLIENT_Y_OFFSET) if self.selected_window else 0
                client_info = f"x: {client_x:<4} y: {client_y:<4} w: {client_w:<4} h: {client_h:<4} (recommended)"
                
                # test_data
                
                # # ratio
                # pct_x = window_h / mouse_x if mouse_x != 0 else 0
                # pct_y = window_w / mouse_y if mouse_y != 0 else 0
                
                # # points
                # rel_x = window_w / pct_x if pct_x != 0 else 0
                # rel_y = window_h / pct_y if pct_y != 0 else 0
                
                # ratio_info = f"x: {pct_x:.4f} y: {pct_y:.4f}"
                # relative_info = f"x: {rel_x:.4f} y: {rel_y:.4f}"
                                
                
                # those magic numbers came from  from testing positions on my native resolution which is 1920x1080
                
                # window_w / 1628 = 1,1891
                # window_h / 991 = 1,0575
                # print(f'mx: {client_x} my: {client_y} w: {window_w} h: {window_h}')
                magic_x = 1.1891
                magic_y = 1.0575
                
                magic_from_source = window_w / client_x if client_x != 0 else 0
                magic_from_source_y = window_h / client_y if client_y != 0 else 0
                mi = f"x: {magic_x:.4f} y: {magic_y:.4f}"
                mfsi = f"x: {magic_from_source:.4f} y: {magic_from_source_y:.4f}"
                            
                rel_x = window_w / 1.1891
                rel_y = window_h / 1.0575
                relative_info = f"x: {rel_x:.4f} y: {rel_y:.4f}"
                
                # now transforming this relative coordinate into absolute for my monitor
                abs_x = rel_x + self.selected_window.left + CLIENT_X_OFFSET
                abs_y = rel_y + self.selected_window.top + CLIENT_Y_OFFSET
                abs_info = f"x: {abs_x:.4f} y: {abs_y:.4f}"
                
                self.tooltip("1", 200, 100, f'  MI: {mi}')
                self.tooltip("2", 200, 200, f'MFSI: {mfsi}')

                
            elif self.selected_window and self.selected_window.isMinimized:
                window_info = client_info = ratio_info = relative_info = abs_info = mi = mfsi = "Minimized"
            else:
                window_info = client_info = ratio_info = relative_info = abs_info = mi = mfsi = "Not selected"

            

            mouse_info = (
                f"Screen: {screen_info}\n"
                f"Window: {window_info}\n"
                f"Client: {client_info}\n"
                # f"Ratio: {ratio_info}\n"
                f"Relative: {relative_info}\n"
                f"Absolute: {abs_info}\n"
                f"\n  MI: {mi}\n"
                f"MFSI: {mfsi}\n"
            )
            self.update_label(self.mouse_info_label, mouse_info)
        else:
            self.update_label(self.mouse_info_label, "Mouse is not being followed")
        
    def update_tooltip_visibility(self):
        if not self.tooltips: return # no tooltips to process
        should_show = self.tooltip_toggle.get()
        
        for tooltip in self.tooltips.values():
            window = tooltip['window']
            # Verifica se o estado atual é diferente do desejado
            if should_show and not window.winfo_viewable():  # Se deve mostrar, mas está oculto
                print(f"update_tooltip_visibility: showing {tooltip}")
                window.deiconify()
            elif not should_show and window.winfo_viewable():  # Se deve ocultar, mas está visível
                print(f"update_tooltip_visibility: hiding {tooltip}")
                window.withdraw()                
        
    # ==================================================================================================== #
    # Widgets 
    
    def tooltip(self, name, x, y, text=""):
        """Cria ou atualiza uma tooltip com base no nome e posição."""
    
        if not self.tooltip_toggle.get(): return # tooltips are disabled, just skip and create this later when you enable it again
        
        if name not in self.tooltips:
            # Se não existir, cria uma nova tooltip
            print('creating tooltip')
            self.create_tooltip(name, x, y, text)
        else:
            self.counter += 1
            if self.counter % 5 == 0:
                print(f'{self.counter} tooltip update count')
                
            tooltip = self.tooltips[name]
            
            # decidindo o que atualizar
            # @NOTE(adrian) there is some optimization techniques we can use to avoid unnecessary updates here
            # like storing the width and height once we discover it, and if text didnt change, we wont need to
            # request width and height again: the label did not change for us to have to check it again
            # .. also theres more stuff possible to do. work your head a bit and see what you can do if this
            # becomes a problem
            
            # deciding what to update
            if text != "" and tooltip['label'].cget("text") != text: 
                # text, size and pos
                self.update_label(tooltip['label'], text)  # text
                label_width = tooltip['label'].winfo_reqwidth()
                label_height = tooltip['label'].winfo_reqheight() 
                tooltip['window'].geometry(f"{label_width}x{label_height}+{x}+{y}") # size and pos
            elif text != "":
                # size and pos
                label_width = tooltip['label'].winfo_reqwidth()
                label_height = tooltip['label'].winfo_reqheight()
                tooltip['window'].geometry(f"{label_width}x{label_height}+{x}+{y}") # size and pos
            else:
                # pos
                tooltip['window'].geometry(f"5x5+{x}+{y}") # pos only, size fixed at 5x5
                
    # ==================================================================================================== #
    # Events 
    
    def on_configure_canvas(self, event, canvas, scroll_x):
        # Atualiza o scrollregion do canvas
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Verifica se a rolagem horizontal é necessária
        if canvas.bbox("all")[2] > canvas.winfo_width():
            # Se o conteúdo exceder a largura, mostra o scroll_x
            scroll_x.pack(side="bottom", fill="x")
        else:
            # Caso contrário, desabilita o scroll_x
            scroll_x.pack_forget()
    
    def on_mouse_scroll(self, event, canvas, horizontal=False):
        if horizontal:
            # Permitir rolagem horizontal apenas se o conteúdo ultrapassar a largura
            if canvas.bbox("all")[2] > canvas.winfo_width():
                canvas.xview_scroll(-1 * (event.delta // 120), "units")
        else:
            # Permitir rolagem vertical apenas se o conteúdo ultrapassar a altura
            if canvas.bbox("all")[3] > canvas.winfo_height():
                canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def on_close(self):
        self.running = False
        self.root.destroy()
    
    # ==================================================================================================== #
    # Binds 
    
    def bind_mouse_scroll(self, canvas):
        # Adiciona o evento para a rolagem horizontal com Shift + MouseWheel
        canvas.bind_all("<Shift-MouseWheel>", lambda e: self.on_mouse_scroll(e, canvas, horizontal=True))
        # Adiciona o evento para a rolagem vertical normal
        canvas.bind_all("<MouseWheel>", lambda e: self.on_mouse_scroll(e, canvas, horizontal=False))

    def unbind_mouse_scroll(self, canvas):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Shift-MouseWheel>")
        

if __name__ == "__main__":
    root = tk.Tk()
    app = WindowSpy(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
