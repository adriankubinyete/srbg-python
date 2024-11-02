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


class System:
    
    
    def __init__(self):
        # tesseract things
        self.TESSERACT_INSTALL_PATH = r'C:\Program Files\Tesseract-OCR'
        self.TESSERACT_COMMAND = self.TESSERACT_INSTALL_PATH + r'\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = self.TESSERACT_COMMAND
        
        # general things
        self.mouse = None

        self.keyboard = None
        self.event_loop = asyncio.new_event_loop() # its for stopping the application later on. this is bizarre but works. dont ask. 
        
        # related to keyboard shortcuts (key combinations)
        keyboard.on_press(self._on_key_press)
        self.key_callbacks = {}
        self.register_shortcut(CONFIGURATION.shortcuts['STOP_APPLICATION'], self.__stop_application)
        self.register_shortcut(CONFIGURATION.shortcuts['OCR_SCREENSHOT_TEST'], self.__ocr_screenshot_test)
        
        
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
        
    # --- SCREENSHOTS RELATED -------------------------------------------------------
    
    
    ''' 
    top_left = [x, y]
    bottom_right = [x, y]
    example: screenshot( [100,200], [200,300] )
    '''
    def screenshot(self, top_left, bottom_right):
        # extract coordinates
        left, top = top_left
        right, bottom = bottom_right
        
        # rounding, just in case
        left = round(left)
        right = round(right)
        top = round(top)
        bottom = round(bottom)
        
        # calculate width and height based on coordinates
        width = right - left
        height = bottom - top

        with mss.mss() as sct:
            # region to capture
            region = {
                "top": top,
                "left": left,
                "width": width,
                "height": height
            }
            
            # actually captures
            screenshot = sct.grab(region)
            
            
            # transforms the image in a np array
            img = np.array(screenshot)
            if img.size == 0:
                # we cant convert the channels of an empty image, so if the image is really empty, we just throw. probably tried screenshotting a minimized window
                raise Exception(f"Screenshot area is out of bounds! {region}")

            # transforms from RGBA to BGR, because OpenCV works with BGR by default
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
            return {
                "region": region,
                "image": img_bgr
            }


    '''
    screenshot : complete self.screenshot() dictionary.
    base_image_path : file path to image for matching in screenshot
    respect: roblox window size to determine if we need to rescale the base image. should be a dictionary containing width and height
    TODO(adrian): make this deal with scaling issues. base images are on 1920x1080, but screenshots can be on different resolutions and match should account for that
        '''
    def find_image_in_screenshot(self, screenshot, base_image_path, respect, threshold=0.81):
        
        '''
        template_image : path to template image
        template_size  : dictionary {width, height}
        target_size    : dictionary {width, height}
        '''
        def resize_template_to_aspect_ratio(template_image, template_size, target_size):
            template_image = cv2.imread(base_image_path)
            TEMPLATE_ASPECT_RATIO = template_size['width'] / template_size['height']
            TARGET_ASPECT_RATIO = target_size['width'] / target_size['height']
            
            print(f"DEBUG: TEMPLATE_ASPECT_RATIO: {TEMPLATE_ASPECT_RATIO}")
            print(f"DEBUG: TARGET_ASPECT_RATIO: {TARGET_ASPECT_RATIO}")
            
            # check if we have to mess with the aspect ratio of the image
            if TARGET_ASPECT_RATIO > TEMPLATE_ASPECT_RATIO:
                SCALE_FACTOR = target_size['height'] / template_size['height']
            else:
                SCALE_FACTOR = target_size['width'] / template_size['width']
            
            # resize the image if needed, and return
            NEW_WIDTH = int(template_image.shape[1] * SCALE_FACTOR)
            NEW_HEIGHT = int(template_image.shape[0] * SCALE_FACTOR)
            
            RESIZED_TEMPLATE_IMAGE = cv2.resize(template_image, (NEW_WIDTH, NEW_HEIGHT))
            
            return RESIZED_TEMPLATE_IMAGE
            
        REGION = screenshot['region']
        IMAGE = screenshot['image']
        RESPECT = respect

        # beware: im assuming every template was made on 1920x1032 (aka 1920x1080 with taskbar and header)
        resized_base_image = resize_template_to_aspect_ratio(base_image_path, {"width": 1920, "height": 1032}, RESPECT)

        #converting both to grayscale
        gray_screenshot = cv2.cvtColor(IMAGE, cv2.COLOR_RGB2GRAY)  # Screenshot em RGB
        gray_base_image = cv2.cvtColor(resized_base_image, cv2.COLOR_BGR2GRAY)  # Template em BGR

        # #dimensions of resized image
        base_height, base_width = gray_base_image.shape

        # #actual matching
        # result = cv2.matchTemplate(gray_screenshot, gray_base_image, cv2.TM_CCOEFF_NORMED)

        # Actual matching using color images
        result = cv2.matchTemplate(IMAGE, resized_base_image, cv2.TM_CCOEFF_NORMED)

        #best match. // max_val = confidence
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # get coordinates of the best match
        top_left = max_loc
        bottom_right = (top_left[0] + base_width, top_left[1] + base_height)

        # calculating the absolute coordinate box of the match
        absolute_top_left = (top_left[0] + REGION['left'], top_left[1] + REGION['top'])
        absolute_bottom_right = (bottom_right[0] + REGION['left'], bottom_right[1] + REGION['top'])
        
        # calculating the center of that "match-box"
        absolute_center_x = (absolute_top_left[0] + absolute_bottom_right[0]) // 2
        absolute_center_y = (absolute_top_left[1] + absolute_bottom_right[1]) // 2
        CENTER = {'x': absolute_center_x, 'y': absolute_center_y}
        
        # Verificar se está acima do threshold de confiança
        if max_val >= threshold:
            return {
                'found': True,
                'screenshot': screenshot,
                'match': {
                    'confidence': {
                        'value': max_val,
                        'threshold': threshold
                    },
                    'coordinates': {  # Representa a posição absoluta
                        'top_left': absolute_top_left,
                        'bottom_right': absolute_bottom_right,
                        'center': CENTER
                    },
                }
            }
        else:            
            return {
                'found': False,
                'screenshot': screenshot,
                'match': {
                    'confidence': {
                        'value': max_val,
                        'threshold': threshold
                    },
                    'coordinates': {  # Representa a posição absoluta
                        'top_left': absolute_top_left,
                        'bottom_right': absolute_bottom_right,
                        'center': CENTER
                    },
                }
            }


    '''
    shows your screenshot in a new window and wait for keypress to continue application
    if you pass data arg, it will be displayed below the screenshot
    example: self.show_screenshot(screenshot, ocr_result, title="--- ocr ---")
    '''
    def show_screenshot(self, screenshot, data=None, title="--- screenshot data ---"):
        IMAGE = screenshot['image']
        # Display the screenshot
        if data:
            # Define default values
            base_font_scale = 1.0
            font_thickness = 2
            text_color = (255, 255, 255)  # White for data text
            initial_text_color = (0, 255, 0)  # Green for initial text
            
            # Calculate the original width and height for the screenshot
            original_width = IMAGE.shape[1]
            original_height = IMAGE.shape[0]

            # Split the data into lines
            data_lines = data.split('\n')

            # Calculate the maximum width for the title and data
            max_text_width = max(
                cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, base_font_scale, font_thickness)[0][0],  # Width of title
                *[cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, base_font_scale, font_thickness)[0][0] for line in data_lines]  # Width of each data line
            )

            # Use the maximum width calculated for the text image
            new_width = max(max_text_width, original_width)

            # Create a black image for the text with the new width
            total_text_height = len(data_lines) * (30) + 50  # Approximate height needed for text
            text_img = np.zeros((total_text_height + 40, new_width, 3), dtype=np.uint8)  # +40 for spacing

            # Initial text position
            y_offset = 40  # Starting Y position for the initial title

            # Add initial text at the top in green
            initial_text_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, base_font_scale, font_thickness)[0]
            initial_text_x = (new_width - initial_text_size[0]) // 2  # Center the initial text
            cv2.putText(text_img, title, (initial_text_x, y_offset), cv2.FONT_HERSHEY_SIMPLEX, base_font_scale, initial_text_color, font_thickness)

            # Reset y_offset for data lines
            y_offset += 40  # Move down to below the initial text

            for line in data_lines:
                # Render each line of text in the text image
                text_x = (new_width - cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, base_font_scale, font_thickness)[0][0]) // 2  # Center the text
                cv2.putText(text_img, line, (text_x, y_offset), cv2.FONT_HERSHEY_SIMPLEX, base_font_scale, text_color, font_thickness)
                y_offset += 30  # Move down for the next line

            # Combine the screenshot and the text image vertically
            # Ensure that the screenshot remains the same size
            combined_height = IMAGE.shape[0] + text_img.shape[0]
            combined_img = np.zeros((combined_height, new_width, 3), dtype=np.uint8)  # Create an empty canvas with the new width
            
            # Place the screenshot at the top
            combined_img[:original_height, :original_width] = IMAGE
            
            # Place the text image below the screenshot
            combined_img[original_height:, :new_width] = text_img

        else:
            combined_img = IMAGE

        # Show the combined image (screenshot + text if present)
        cv2.imshow('Screenshot', combined_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    '''
    result: return from self.find_image_in_screenshot()
    Displays the result on screen. Only for debug purposes.
    '''
    def display_match_from_screenshot(self, result):
        screenshot = result['screenshot']
        IMAGE = screenshot['image']
        REGION = screenshot['region']
        IS_FOUND = result['found']
        
        # the coordinates must be relative to the screenshot, so we will convert them from absolute to relative
        absolute_top_left = result['match']['coordinates']['top_left']
        absolute_bottom_right = result['match']['coordinates']['bottom_right']
        
        relative_top_left = (
            absolute_top_left[0] - REGION['left'],
            absolute_top_left[1] - REGION['top']
        )
        
        relative_bottom_right = (
            absolute_bottom_right[0] - REGION['left'],
            absolute_bottom_right[1] - REGION['top']
        )
        
        # drawing a rectangle around the found template
        cv2.rectangle(IMAGE, relative_top_left, relative_bottom_right, (0, 255, 0), 2)  # Green rectangle with 2px thickness
        
        # displaying the confidence level
        cv2.putText(IMAGE, f"Found: {IS_FOUND}, Confidence: {result['match']['confidence']['value']:.2f}", (relative_top_left[0], relative_top_left[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Show the result
        cv2.imshow("Matched Image", IMAGE)
        cv2.waitKey(0)  # Wait for a key press
        cv2.destroyAllWindows()


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
