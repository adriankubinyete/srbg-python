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
        
        self.create_tab(parent_frame)

    def _add_setting(self, parent_frame, key, value, parent_config):
        """
        Adds a label and an entry field for a single setting.
        :param parent_frame: The parent frame to add the widgets.
        :param key: The setting's key.
        :param value: The setting's value.
        :param parent_config: Reference to the parent config dictionary.
        """
        row = parent_frame.grid_size()[1]  # Calculate current row based on grid
        tk.Label(parent_frame, text=key).grid(row=row, column=0, sticky="w", padx=10, pady=1)

        # Create a text field to display and edit the value
        text_var = tk.StringVar(value=value if value is not None else "")
        entry = tk.Entry(parent_frame, textvariable=text_var)
        entry.grid(row=row, column=1, sticky="ew", padx=10, pady=1)

        # Save the text_var and its path to config for later use
        self.entry_refs.append((text_var, parent_config, key))

        # Allow the entry column to expand horizontally
        parent_frame.columnconfigure(1, weight=1)

    def _iterate_properties(self, properties, parent_config, parent_frame):
        """
        Recursively iterates over the configuration properties and creates widgets.
        :param properties: Dictionary of properties to iterate over.
        :param parent_config: Reference to the parent config dictionary.
        :param parent_frame: The parent frame to add widgets.
        """
        for key, value in properties.items():
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
                self._iterate_properties(value, parent_config[key], group_frame)
            else:
                self._add_setting(parent_frame, key, value, parent_config)

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

        # Create the settings widgets inside the scrollable frame
        self._iterate_properties(self.config, self.config, scrollable_frame)

        # Add a "Save" button at the bottom of the scrollable frame
        save_button = tk.Button(scrollable_frame, text="Save", command=self._save_changes)
        save_button.grid(row=scrollable_frame.grid_size()[1], column=0, columnspan=2, padx=10, pady=10, sticky="ew")

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

    def _save_changes(self):
        """
        Saves all changes from text fields back to the config.
        """
        for text_var, parent_config, key in self.entry_refs:
            parent_config[key] = text_var.get() or None
        print("Config updated:", self.config)  # Debugging log or replace with actual saving logic
