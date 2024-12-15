# for screenshot and image searching
import cv2
import numpy as np
import mss
# for process manipulation
import subprocess
# for ocr
import pytesseract # needs tesseract installed locally!
from PIL import Image, ImageEnhance, ImageFilter
# for doing user input
import pydirectinput
# other things
from difflib import SequenceMatcher
from screeninfo import get_monitors
import time
import keyboard
import asyncio
# local lib
from lib.configuration import CONFIGURATION
from utils.screenutils import ScreenUtils


class System(ScreenUtils):
    
    
    def __init__(self):
        super().__init__()
        
        # general things
        self.mouse = None

        self.keyboard = None
        self.event_loop = asyncio.new_event_loop() # its for stopping the application later on. this is bizarre but works. dont ask. 
        
        # related to keyboard shortcuts (key combinations)
        keyboard.on_press(self._on_key_press)
        self.key_callbacks = {}
        self.register_shortcut(CONFIGURATION.shortcuts['STOP_APPLICATION'], self.__stop_application)
        # self.register_shortcut(CONFIGURATION.shortcuts['OCR_SCREENSHOT_TEST'], self.__ocr_screenshot_test)
        
        
    # --- TEST KEY MONITORING -----------------------------------------------
 
    def __ocr_screenshot_test(self):
        POINT_ONE = None
        POINT_TWO = None
        SHORTCUT = CONFIGURATION.shortcuts['OCR_SCREENSHOT_TEST']
        
        # register the first point. edit the shortcut to call the next step
        def take_point_one():
            nonlocal POINT_ONE
            POINT_ONE = self.get_mouse_position()
            print('DEBUG: Point one: ', POINT_ONE)

            self.register_shortcut(SHORTCUT, take_point_two) # if ran again, do the next step
        
        # register the second point and show the screenshot. edit the shortcut to re-do the function
        def take_point_two():
            nonlocal POINT_TWO
            POINT_TWO = self.get_mouse_position()
            print('DEBUG: Point two: ', POINT_TWO)
            
            ss = self.screenshot(POINT_ONE, POINT_TWO)
            ocr = self.ocr_from_screenshot(ss, apply_filters=False)
            self.show_screenshot(ss, ocr)
            
            self.register_shortcut(SHORTCUT, self.__ocr_screenshot_test)
            
        take_point_one()
 
 
 
    # callback to stop the application
    # this could probably be implemented better, but oh well
    def __stop_application(self):
        print(f"Stopping application...")

        # you need to call the main function of what youre running using our own event loop
        # then i can reference it here and stop if you pressed the right combination for this callback
        for task in asyncio.all_tasks(self.event_loop):
            task.cancel()
    
    
    # make a key combination
    def register_shortcut(self, key_combination, callback):
        self.key_callbacks[key_combination] = callback
    
    
    # every key pressed, do this
    def _on_key_press(self, event):
        PRESSED_KEY = event.name
        # print('DEBUG: Pressed key:', PRESSED_KEY)
        
        #mapping the active keys
        active_keys = []
        if keyboard.is_pressed('ctrl') or keyboard.is_pressed('right ctrl'):
            active_keys.append('ctrl')
        if keyboard.is_pressed('shift') or keyboard.is_pressed('right shift'):
            active_keys.append('shift')
        if keyboard.is_pressed('alt'):
            active_keys.append('alt')
            
        combined_key = '+'.join(active_keys + [PRESSED_KEY])
        
        # calling the callback
        if combined_key in self.key_callbacks:
            self.key_callbacks[combined_key]()    
    
    # --- INFORMATION -------------------------------------------------------
    
    def get_screen_resolution(self):
        # get the primary monitor
        primary_monitor = get_monitors()[0]
        # get the resolution
        width = primary_monitor.width
        
        
    def get_monitors(self):
        return get_monitors()
    
    
    # keep your roblox on a single display... dont put your roblox in the middle of two screens...
    # I will NOT code to account for that. with love, fuck you.
    def find_monitor(self, window):
        window_x = window['x']
        window_y = window['y']
        window_width = window['width']
        window_height = window['height']

        # Obtenha a lista de monitores
        monitors = self.get_monitors()

        # Verifica em qual monitor a janela está
        for monitor in monitors:
            if (monitor.x <= window_x <= monitor.x + monitor.width) and \
               (monitor.y <= window_y <= monitor.y + monitor.height):
                return monitor
        
        return None  # Caso nenhum monitor seja encontrado
        
    # --- OCR RELATED -------------------------------------------------------
    
    '''
    screenshot: from self.screenshot['image']
    strength: filter strength. default 1
    '''
    def screenshot_ocr_enhancement(self, screenshot, filter_strength=1, enlarge=True, matrix=True, grayscale=True, blur=False):
        
        def apply_color_matrix(image, matrix):
            #checking if it has 4 channels (RGBA)
            if image.shape[2] != 3:
                raise ValueError(f"A imagem precisa ter 3 canais (RGBA). ({image.shape[2]})")

            #acessing image's data
            data = image.reshape((-1, 3))  #redefining to an Nx4 (r, g, b, a) matrix

            #apply the color matrix
            for i in range(len(data)):
                r, g, b = data[i]
                new_r = np.clip(matrix[0] * r + matrix[1] * g + matrix[2] * b, 0, 255)
                new_g = np.clip(matrix[3] * r + matrix[4] * g + matrix[5] * b, 0, 255)
                new_b = np.clip(matrix[6] * r + matrix[7] * g + matrix[8] * b, 0, 255)
                data[i] = [new_r, new_g, new_b]

            #redefine the data
            return data.reshape(image.shape)
        
        
        if matrix:
            color_matrix = [
                2, 0, 0,   # Red
                0, 1.5, 0, # Green
                0, 0, 1,   # Blue
            ]
            screenshot = apply_color_matrix(screenshot, color_matrix)
            
        if grayscale:
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
        
        if blur:
            screenshot = cv2.medianBlur(screenshot, 1) # blur
        
        if enlarge:
            height, width = screenshot.shape[:2]
            new_width = int(width + (filter_strength * 38))
            new_height = int(height + (filter_strength * 7.5))
            # print('Enlarging to', new_width, 'x', new_height, 'with strength of', filter_strength)
            screenshot = cv2.resize(screenshot, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            
        
        return screenshot  
    
    
    '''
    returns the text, read from screenshot
    ps: it does some enhancement before doing the actual OCR.
    '''
    def ocr_from_screenshot(self, screenshot, apply_filters=True, filter_strength=1):
        IMAGE = screenshot['image']
        
        if apply_filters: IMAGE = self.screenshot_ocr_enhancement(IMAGE, filter_strength=filter_strength, enlarge=True, matrix=True, grayscale=False, blur=False)
        
        text = pytesseract.image_to_string(IMAGE)
        return text
    
    
    # --- PROCESS RELATED -------------------------------------------------------

    '''
    command : string with command to be executed
    example: self._execute_command("taskkill /im python.exe /f")
    '''
    async def _execute_command(self, command):
        try:
            # Executa o comando do sistema
            subprocess.run(command, check=True, shell=True)
        except subprocess.CalledProcessError as error:
            # Lança exceção se o comando falhar
            raise RuntimeError(f"Command failed: {error}")
        
        
    '''
    process_id : int with process id
    example: self.taskkill(12345)
    '''
    async def taskkill(self, process_id):
        try:
            # Executa o comando taskkill com o ID do processo
            await self._execute_command(f"taskkill /F /PID {process_id}")
        except Exception as error:
            raise RuntimeError(f"Failed to kill process {process_id}: {error}")
    
    
    '''
    url : string with url to be opened
    example: self.start_url("roblox://placeID=15532962292&linkCode=83338549084739556308838773836658")
    '''
    async def start_url(self, url):
        try:
            # Executa o comando para abrir a URL no navegador padrão
            await self._execute_command(f'start "" "{url}"')
        except Exception as error:
            raise RuntimeError(f"Failed to start url {url}: {error}")
        
    # --- INPUT RELATED -------------------------------------------------------
    
    def get_mouse_position(self):
        return pydirectinput.position()
    
    # pyautogui doesnt work: https://www.youtube.com/watch?v=LFDGgFRqVIs
    # also, we cant just teleport to destination. we have to do a bit of moving there so it properly registers the mouse
    # ^ dont ask me why
    async def mouse_move(self, x, y, wiggle_distance=3, delay=0.05):
        
        # we will cast to int here, pydirectinput doesnt handle floats
        x = int(x)
        y = int(y)
        
       # teleports to objective
        pydirectinput.moveTo(x, y)
        
        # wait a tiny bit
        time.sleep(delay)
        
        # move a bit, wait, and return to objective
        pydirectinput.moveTo(x + wiggle_distance, y + wiggle_distance)
        time.sleep(delay)
        pydirectinput.moveTo(x, y)

    async def mouse_click(self, x=None, y=None, button='left', click_delay=0.2):
        if x is None or y is None:
            print('CLICKING BECAUSE X OR Y IS NONE')
            return pydirectinput.click(button=button)

        await self.mouse_move(x, y)
        time.sleep(click_delay)
        print(f"--- DEBUG: DE FACTO, CLICKING: [{x}, {y}] ---")
        pydirectinput.click(int(x), int(y), button=button) # we will cast to int here, pydirectinput doesnt handle floats
        

#singleton
System = System()
