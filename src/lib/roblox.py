# window management
import pygetwindow as gw
from pywinauto import mouse
import psutil
import win32process
import win32gui
import win32con
# parse server url
from urllib.parse import urlparse, parse_qs
# other things
import time
import asyncio
from difflib import SequenceMatcher # for string similarity
# local library
from lib.configuration import CONFIGURATION
from lib.system import System

class Roblox:
    
    def __init__(self):
        self.TEMP_FULL_PRIVATE_SERVER = CONFIGURATION.roblox['private_server_link']  # temporary hardcoded, should come from configs
        self.TEMP_ROBLOX_CLOSE_INTERVAL = 10 # seconds
        
        self.ROBLOX_WINDOW_TITLE = "Roblox"
        self.ROBLOX_EXECUTABLE_NAME = "RobloxPlayerBeta.exe"
        self.PRIVATE_SERVER_LINK = None
        
        self.HP_TEMPLATE_TOP_LEFT = None
        self.HP_TEMPLATE_BOTTOM_RIGHT = None
        
        System.register_shortcut(CONFIGURATION.shortcuts['LOG_INFO'], self.__debug_data)

    # --- STATE CHECKS  -------------------------------------------------------

    def isOpen(self):
        
        # gets all windows
        windows = gw.getAllWindows()

        # filters windows that has "Roblox" in title
        roblox_windows = [
            window for window in windows if self.ROBLOX_WINDOW_TITLE in window.title
        ]

        # no windows with title "Roblox"
        if not roblox_windows: return False
        
        # now checks if any of the windows is actually the roblox executable
        for roblox_window in roblox_windows:
            hwnd = roblox_window._hWnd
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)

            try:
                # process associated with that id
                process = psutil.Process(process_id)
                path = process.exe()  #executable path

                # if the path is the roblox executable, then we found the correct roblox window
                if self.ROBLOX_EXECUTABLE_NAME in path: return True

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue  # Ignora janelas que não podem ser acessadas

        # we looped over all "Roblox" titled window, but couldnt find anything: roblox is not open
        return False


    async def isChatOpen(self, show_match=False, show_screenshot=False):
        CHAT_OPEN_TEMPLATE = r"src\images\match\template_chat.png"
        CHAT_BUTTON = self.get_chat_button_position()
        top_left = self.absolute_from_relative(CHAT_BUTTON['position'][0][0], CHAT_BUTTON['position'][0][1])
        bottom_right = self.absolute_from_relative(CHAT_BUTTON['position'][1][0], CHAT_BUTTON['position'][1][1])    
        
        screenshot = System.screenshot([top_left['x'], top_left['y']], [bottom_right['x'], bottom_right['y']])
        result = System.find_image_in_screenshot(screenshot["image"], screenshot["region"], CHAT_OPEN_TEMPLATE, threshold=0.9)
        
        if show_match:
            System.display_match_from_screenshot(result)
            
        if show_screenshot:
            System.show_screenshot(screenshot["image"])
        
        return result
    


    # --- utilitary / preparation -------------------------------------------------------
    
    # basically gets some useful data
    # System.register_shortcut('ctrl+2', self.__debug_data)
    def __debug_data(self):
        
        # not used anymore
        # def calculate_target_y(window_width, window_height):
        #     data_points = [
        #         (3692, 1084, 32.6),
        #         (1920, 1032, 32.8),
        #         (2643, 905, 33.0),
        #         (1275, 715, 33.4),
        #         (2643, 715, 33.4)
        #     ]
        #     # data_points é uma lista de tuplas contendo (width, height, y_dfc)
        #     target_y = 0
        #     for width, height, y_dfc in data_points:
        #         # Calcular a posição Y baseada no YDFC
        #         calculated_y = (y_dfc / 100) * height
        #         # Armazenar a relação da altura
        #         target_y += calculated_y * (window_height / height)
        #     # Retornar a média das posições Y calculadas
        #     return target_y / len(data_points)
            
        # asserting roblox window size
        roblox = self.window()
        roblox_position = roblox['bounds']
        x = roblox_position['x']
        y = roblox_position['y']
        width = roblox_position['width']
        height = roblox_position['height']
        
        # obtaining current mouse position
        mouse_pos = System.get_mouse_position()
        mouseX = mouse_pos[0]
        mouseY = mouse_pos[1]

        # calculating the relative position of mouse from roblox window
        relativeX = ((mouseX - x) / width) * 100 # % width
        relativeY = ((mouseY - y) / height) * 100 # % height
        
        # returning informations
        print(f"                       Absolute :   {mouseX}, {mouseY}")
        print(f"                       Relative :   {(relativeX / 100) * width}, {(relativeY / 100) * height}")
        print(f"                     Relative % :   {relativeX}, {relativeY}")
        print(f"    Distance from Roblox Center :   {x + width / 2 - mouseX}, {y + height / 2 - mouseY}")
        print(f"                   Aspect Ratio :   {width / height}")
        # print(f"#{i}         Roblox Center location :   {x + width / 2}, {y + height / 2}")
        print(f"           Roblox width, height :   {width}, {height}")
        print('') # new line    
    
    
    def show_window(self):
        ROBLOX = self.window()
        ROBLOX_BOUNDS = ROBLOX['bounds']
        print(ROBLOX)
        screenshot =  System.screenshot([ROBLOX_BOUNDS['x'], ROBLOX_BOUNDS['y']], [ROBLOX_BOUNDS['x']+ROBLOX_BOUNDS['width'], ROBLOX_BOUNDS['y']+ROBLOX_BOUNDS['height']])
        System.show_screenshot(screenshot["image"])
    
    
    def _get_private_server (self):
        
        # if it already exists, return
        if self.PRIVATE_SERVER_LINK: return self.PRIVATE_SERVER_LINK
        
        # else, create from config
        FULL_URL_PRIVATE_SERVER = self.TEMP_FULL_PRIVATE_SERVER # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< UPDATE THIS BEFORE DEPLOYING (FROM CONFIG)
        
        # prepare the actual link thats used in the start cmd
        PARSED_PRIVATE_SERVER = urlparse(FULL_URL_PRIVATE_SERVER)
        PRIVATE_SERVER_CODE = parse_qs(PARSED_PRIVATE_SERVER.query).get("privateServerLinkCode", [None])[0]  
        PRIVATE_SERVER_LINK = f"roblox://placeID=15532962292&linkCode={PRIVATE_SERVER_CODE}" # this
        self.PRIVATE_SERVER_LINK = PRIVATE_SERVER_LINK
        return PRIVATE_SERVER_LINK
    
    
    async def _wait_server_disconnect_interval(self):
        # you have to wait a bit before starting roblox again
        # else roblox will flag "Login from another device"
        # didnt test this throughly, but it should be about 5~10 seconds. default 10 seconds
        print(f"Waiting for a clean disconnect... ({self.TEMP_ROBLOX_CLOSE_INTERVAL} seconds)")
        await asyncio.sleep(self.TEMP_ROBLOX_CLOSE_INTERVAL)
        return
        
        
    def absolute_from_relative_percent(self, relative_x, relative_y):
        roblox = self.window()  # Obtenha as informações da janela do Roblox
        roblox_bounds = roblox['bounds']  # Contém x, y, width e height

        # Calcula as coordenadas absolutas
        x = int((relative_x / 100) * roblox_bounds['width'] + roblox_bounds['x'])
        y = int((relative_y / 100) * roblox_bounds['height'] + roblox_bounds['y'])

        return {'x': x, 'y': y}


    def absolute_from_relative(self, relative_x, relative_y):
        roblox = self.window()  # Obtenha as informações da janela do Roblox
        roblox_bounds = roblox['bounds']  # Contém x, y, width e height

        # Calcula as coordenadas absolutas
        x = int(relative_x + roblox_bounds['x'])
        y = int(relative_y + roblox_bounds['y'])

        return {'x': x, 'y': y}
    
    
    # --- ELEMENT POSITIONS -------------------------------------------------------
    
    # returns ABSOLUTE x,y that represents the center of the Nth menu button
    # TODO(adrian)(critical): THIS IS A SERIOUS PROBLEM! MAYBE USE IMAGE-MATCHING?
    # Differente resolutions will have problems on clicking the correct spot. Maybe use image matching to fix this?
    def get_side_menu_button_position(self, num):
        # 1: storage,  2: collection,  3: inventory,       4: achievements
        # 5: quests,   6: settings,    7: pvt management,  8: gamepass

        # in theory, you should always be on a pvt server!!! <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< FIXME LATER
        num = num if True else num + 1

        # getting roblox window size
        ROBLOX = self.window()
        ROBLOX_BOUNDS = ROBLOX['bounds']
        
        print('Roblox Bounds: ', ROBLOX_BOUNDS)
        # needs to get monitor's width and height
        monitor = System.find_monitor(ROBLOX_BOUNDS)

        # offsets
        menu_bar_offset = 20   # x deviation from left border from rblx window

        # calculating spacing and button size based on roblox window resolution
        spacing_size_var = 10.5 * ((ROBLOX_BOUNDS['width'] / monitor.width) * (ROBLOX_BOUNDS['height'] / monitor.height))**0.5
        button_size_var = 58.0 * ((ROBLOX_BOUNDS['width'] / monitor.width) * (ROBLOX_BOUNDS['height'] / monitor.height))**0.5

        # vertical spacing
        menu_bar_v_spacing = spacing_size_var * (ROBLOX_BOUNDS['height'] / monitor.height)
        
        # button sizes
        menu_bar_button_size = button_size_var * (ROBLOX_BOUNDS['width'] / monitor.width)

        print(f"Menu Bar Vertical Spacing: {menu_bar_v_spacing}")
        print(f"Menu Bar Button Size: {menu_bar_button_size}")

        # menu center on left border
        menu_edge_center_x = ROBLOX_BOUNDS['x'] + menu_bar_offset
        menu_edge_center_y = ROBLOX_BOUNDS['y'] + (ROBLOX_BOUNDS['height'] / 2)

        # first button initial position
        start_pos_x = menu_edge_center_x + (menu_bar_button_size / 2)
        start_pos_y = menu_edge_center_y + (menu_bar_button_size / 4) - (menu_bar_button_size + menu_bar_v_spacing - 1) * 3.5

        # calculating the position of the specific button based on "num"
        pos_x = start_pos_x
        pos_y = start_pos_y + (menu_bar_button_size + menu_bar_v_spacing) * (num - 0.5)

        print(f"Menu Button Position: {num} ({pos_x}, {pos_y})")

        # returns the NUMth button's position
        return {'x': pos_x, 'y': pos_y}
    
    
    # returns ABSOLUTE position and center
    def get_play_button_position(self):


        # nbew positions, transform this to fit with this class'p positions <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # top = (self.selected_window.top + CLIENT_Y_OFFSET) + int(window_h / 1.7643)
        # left = (self.selected_window.left + CLIENT_X_OFFSET) + int(window_w / 3.3437)
        # bottom = self.selected_window.top + self.selected_window.height - CLIENT_Y_OFFSET # bottom of window
        # right = (window_w - left)

        # # obtaining roblox coordinates
        # ROBLOX = self.window()
        # ROBLOX_BOUNDS = ROBLOX['bounds']
        # x = ROBLOX_BOUNDS['x']
        # y = ROBLOX_BOUNDS['y']
        # width = ROBLOX_BOUNDS['width']
        # height = ROBLOX_BOUNDS['height']

        # # calculating center of roblox window
        # center_x = x + width / 2
        # center_y = y + height / 2

        # # rectangle size that contains play button
        # button_width = width * 0.30  # Largura do botão de jogar
        # button_height = height * 0.20  # Altura do botão de jogar

        # # offsets
        # y_offset = height * 0.35

        # # calculates the relative position of the play button around the center, adjusted with offset
        # x1 = center_x - button_width / 2
        # y1 = center_y - button_height / 2 + y_offset
        # x2 = center_x + button_width / 2
        # y2 = center_y + button_height / 2 + y_offset
        
        # # getting button center for click
        # center_button_x = (x1 + x2) / 2
        # center_button_y = (y1 + y2) / 2

        # # return as dictionary
        # return {
        #     'type': 'absolute',
        #     'position': [[x1, y1], [x2, y2]],
        #     'center': { 'x': center_button_x, 'y': center_button_y } # what the actual fuck?
        # }
        
        return {
            'x': '',
            'y': '',
            'width': '',
            'height': '',
            'center': {
                'x':'', 
                'y':''
            },
        }
    
    
    # returns RELATIVE PERCENT center
    def get_auto_roll_button_position(self):
        return {
            'type': 'relative_percent',
            'position': None, # i dont need to know box, just where i will click (aka center)
            'center': { 'x': 38.480, 'y': 94.310 }
        } 
        
        
    # returns RELATIVE PERCENT center
    def get_skip_aura_button_position(self):
        return {
            'type': 'relative_percent',
            'position': None, # i dont need to know box, just where i will click (aka center)
            'center': { 'x': 56.198, 'y': 84.541 }
        }
        
        
    #returns ABSOLUTE center
    def get_close_collection_button_position(self):
        return {
            'type': 'relative_percent',
            'position': None, # i dont need to know box, just where i will click (aka center)
            'center': { 'x': 15.082, 'y': 11.641 }
        }   
    
    
    # returns RELATIVE position
    def get_chat_button_position(self):
        return {
            'type': 'relative',
            'position': [[0, 0], [200, 100]], # this is just the overall area, not the actual chat button definition
            'center': None, # this has to come from image matching because we are just looking on an overall area, not the exact chat button!
        }
    
    
    # --- ROBLOX WINDOW RELATED  (open, close, size, position, etc) -------------------------------------------------------
    
    def window(self):
        WINDOW_X_OFFSET = 8 # (remove invisible shadow)
        WINDOW_Y_OFFSET = 8 # (remove invisible shadow)
        
        # Obtém todas as janelas abertas
        windows = gw.getAllWindows()

        # Filtra as janelas que têm o título "Roblox"
        roblox_windows = [
            window for window in windows if self.ROBLOX_WINDOW_TITLE in window.title
        ]

        # Se não houver janelas, lança uma exceção
        if not roblox_windows:
            raise Exception("Nenhuma janela do Roblox encontrada.")

        # Verifica cada janela do Roblox para encontrar o executável
        for roblox_window in roblox_windows:
            hwnd = roblox_window._hWnd
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)

            try:
                # Obtém o processo associado ao ID
                process = psutil.Process(process_id)
                path = process.exe()  # Caminho do executável

                # Verifica se o executável contém o nome esperado
                if self.ROBLOX_EXECUTABLE_NAME in path:
                    bounds = {
                        # apparently windows adds some shadow around the window?
                        # this adjustment made it PERFECT on my computer.
                        'x': roblox_window.left + WINDOW_X_OFFSET,
                        'y': roblox_window.top + WINDOW_Y_OFFSET,
                        'width': roblox_window.width - (WINDOW_X_OFFSET * 2),
                        'height': roblox_window.height - (WINDOW_Y_OFFSET * 2)
                    }
                    state = {
                        'minimized': roblox_window.isMinimized,
                        'maximized': roblox_window.isMaximized,
                        'foreground': roblox_window.isActive
                    }

                    # Retorna os dados da janela do Roblox
                    data = {
                        'process': process_id,
                        'window': roblox_window,
                        'bounds': bounds,
                        'state': state,
                    }
                    return data

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue  # Ignora janelas que não podem ser acessadas

        # Se nenhuma janela válida for encontrada
        raise Exception("Nenhuma janela do Roblox encontrada com o executável correto.")
    
    
    def bring_to_top(self):
        ROBLOX = self.window()
        ROBLOX_WINDOW = ROBLOX['window']
        
        if not ROBLOX_WINDOW._hWnd:
            raise ValueError("Window handle (_hWnd) is not valid.")

        # FIXME
        # https://stackoverflow.com/a/79067711
        # fuck you windows
        mouse.move(coords=(-10000, 500))
        
        # checks if its minimized
        if ROBLOX_WINDOW.isMinimized:
            win32gui.ShowWindow(ROBLOX_WINDOW._hWnd, win32con.SW_SHOW)
        win32gui.SetForegroundWindow(ROBLOX_WINDOW._hWnd)
        return
    
    
    def maximize(self): 
        # it doesnt make sense to me that you would want to maximize without bringing to foreground, so ill also do that
        ROBLOX = self.window()
        ROBLOX_WINDOW = ROBLOX['window']
        
        self.bring_to_top()
        ROBLOX_WINDOW.maximize()
        return
    
    
    # --- ACTIONS -------------------------------------------------------
    
    async def click(self, x, y, NOTIFY=False, CLICK=True, TYPE='relative'):
        absolute = { 'x': x, 'y': y }
    
        # converting the position given to us, to the adequate absolute value
        if TYPE.lower() == 'relative':
            absolute = self.absolute_from_relative(x, y)
        elif TYPE.lower() == 'relative_percent':
            absolute = self.absolute_from_relative_percent(x, y)
        elif TYPE.lower() == 'absolute':
            pass
        else:
            raise Exception(f"Invalid type: {TYPE}")

        # checking if we should announce what were ding
        if NOTIFY:
            print(f"Roblox.click: \"{absolute}\" (Click:{CLICK})")
            
        # checking if we should only move the mouse, and not click
        if not CLICK:
            return await System.mouse_move(absolute['x'], absolute['y'])
        
        await System.mouse_click(absolute['x'], absolute['y'])    
    
    
    # remember: this will wait the _wait_server_disconnect_interval before actually finishing!
    async def close(self):
        if not self.isOpen(): return
        
        ROBLOX = self.window()
        ROBLOX_PROCESS = ROBLOX['process']
        await System.taskkill(ROBLOX_PROCESS)
        
        while self.isOpen():
            print(f"Waiting for roblox to close...")
            await asyncio.sleep(1)
            
        await self._wait_server_disconnect_interval()
    
    
    # private server to join comes from "self.PRIVATE_SERVER_LINK"
    async def join_private_server(self, force=False):
        self._get_private_server() # prepares the private server link in class

        # checks if its already open
        if self.isOpen():
            if force:
                await self.close()
            else:
                raise RuntimeError("Roblox is already open")
                
        # joins the private server
        print('Joining: ', self.PRIVATE_SERVER_LINK)
        await System.start_url(self.PRIVATE_SERVER_LINK) 
        
        # wait until its actually open
        while not self.isOpen():
            print(f"Waiting for roblox to open...")
            await asyncio.sleep(1)
        
        # brings to foreground and maximizes
        self.maximize()
        print(f"Roblox is open")
        return
    
    
    async def wait_server(self, show_screenshot=False):
        EXPECTED_TEXT = "Waiting for an available server"
        TEXT_SIMILARITY_THRESHOLD = 0.5 # text recognition is dogshit. its so small it messes with tesseract
        CHECKING_INTERVAL_SECONDS = 2 # interval between each check
        TIMEOUT_SECONDS = 60
        MAX_ITERATIONS = 15
        IS_WAITING_SERVER = False
        i = 0
        start_time = time.time()
        
        ROBLOX = self.window()
        ROBLOX_BOUNDS = ROBLOX['bounds']
        
        # position of the rectangle we will be checking
        FINAL_Y_OFFSET = -25
        FINAL_X_OFFSET = 0
        rect_height = 30
        rect_width_percent = 0.25
        rect_width = rect_width_percent * ROBLOX_BOUNDS['width']
        centerX = ROBLOX_BOUNDS['width'] / 2
        centerY = ROBLOX_BOUNDS['height'] / 2
        y1 = round(ROBLOX_BOUNDS['height'] - rect_height + FINAL_Y_OFFSET)
        y2 = round(ROBLOX_BOUNDS['height'] + FINAL_Y_OFFSET)
        x1 = round(centerX - (rect_width / 2) + FINAL_X_OFFSET)
        x2 = round(centerX + (rect_width / 2) + FINAL_X_OFFSET)
        SCREENSHOT_AREA = [(x1, y1), (x2, y2)]
        
        # checking loop
        while i <= MAX_ITERATIONS:
            i += 1
            elapsed_time = time.time() - start_time
            
            # checking if we should stop the loop
            if elapsed_time >= TIMEOUT_SECONDS:
                raise Exception("PLAY_BUTTON: Timeout > Server took too long.")
            if i > MAX_ITERATIONS:
                raise Exception("PLAY_BUTTON: IterationLimit > Max iterations reached.")
    
            # taking screenshot
            screenshot = System.screenshot(SCREENSHOT_AREA[0], SCREENSHOT_AREA[1])
            
            # reading
            ocr_result = System.ocr_from_screenshot(screenshot["image"])
            
            if show_screenshot:
                System.show_screenshot(screenshot["image"], ocr_result.lower(), title="--- ocr: wait for server ---")
                
            
            # calculates text similarity with our expected text
            similarity = SequenceMatcher(None, ocr_result, EXPECTED_TEXT).ratio()
            
            # now we check if it hit our similarity threshold
            if similarity >= TEXT_SIMILARITY_THRESHOLD:
                IS_WAITING_SERVER = True
                print(f"#{i} SIMILARITY: {similarity}, OCR: {ocr_result.replace('\n', '\\n')}")
                print("Waiting server...")
            else:
                IS_WAITING_SERVER = False
                print(f"#{i} SIMILARITY: {similarity}, OCR: {ocr_result.replace('\n', '\\n')}")
                print(f"#{i} We are not waiting for a server anymore!")
                break
            
            # waits a bit before repeating
            await asyncio.sleep(CHECKING_INTERVAL_SECONDS)
            
        return IS_WAITING_SERVER
    
    
    async def wait_play_button(self, click_when_found=True, show_screenshot=False):
        MAX_ITERATIONS = 15
        MAX_TIMEOUT_SECONDS = 15
        INTERVAL_PER_ITERATION = MAX_TIMEOUT_SECONDS / MAX_ITERATIONS
        PLAY_BUTTON_FOUND = False
        PLAY_BUTTON = None
        
        # for i in range(1, MAX_ITERATIONS):
        #     PLAY_BUTTON = self.get_play_button_position()

        #     screenshot = System.screenshot(PLAY_BUTTON['position'][0], PLAY_BUTTON['position'][1])
        #     ocr_result = System.ocr_from_screenshot(screenshot["image"])
            
        #     if show_screenshot:
        #         System.show_screenshot(screenshot["image"], ocr_result.replace('\n','\\n'), title="--- ocr: wait for play button ---")
            
        #     # check if "play" is in the ocr result
        #     if "play" in ocr_result.lower():  # Verifica sem case sensitivity
        #         PLAY_BUTTON_FOUND = True
        #         break
            
        #     print(f"Iteration {i}: Waiting for play button... (OCR: \"{ocr_result}\")")
        #     await asyncio.sleep(INTERVAL_PER_ITERATION)
            
        # if not PLAY_BUTTON_FOUND:
        #     raise Exception("PLAY_BUTTON: Play button was not found!")

        # print(f"#{i} PLAY_BUTTON_FOUND: {PLAY_BUTTON_FOUND}")

        # if click_when_found:
        #     await self.click_play_button()
        # return
        
        for i in range(1, MAX_ITERATIONS):
            PLAY_BUTTON = self.get_play_button_position()
            
            
    async def click_play_button(self):
        PLAY_BUTTON = self.get_play_button_position()
        x = PLAY_BUTTON['center']['x']
        y = PLAY_BUTTON['center']['y']
        await self.click(x, y, TYPE=PLAY_BUTTON['type'])
        
        
    async def click_side_menu_button_position(self, num, check_for_chat=True, chat_show_screenshot=False):
        if check_for_chat:
            await self.close_chat_if_open(show_screenshot=chat_show_screenshot)
            
        MENU_BUTTON = self.get_side_menu_button_position(num)
        print(f"MENU_BUTTON: {MENU_BUTTON}")
        x = MENU_BUTTON['x']
        y = MENU_BUTTON['y']
        await self.click(x, y, TYPE='absolute')
        
        
    async def click_auto_roll_button(self):
        AUTO_ROLL_BUTTON = self.get_auto_roll_button_position()
        x = AUTO_ROLL_BUTTON['center']['x']
        y = AUTO_ROLL_BUTTON['center']['y']
        await self.click(x, y, TYPE=AUTO_ROLL_BUTTON['type'])
    
    
    async def click_skip_aura_button(self):
        SKIP_AURA_BUTTON = self.get_skip_aura_button_position()
        x = SKIP_AURA_BUTTON['center']['x']
        y = SKIP_AURA_BUTTON['center']['y']
        await self.click(x, y, TYPE=SKIP_AURA_BUTTON['type'])
    
    
    async def click_close_collection_button(self, check_for_chat=True, chat_show_screenshot=False):
        if check_for_chat:
            await self.close_chat_if_open(show_screenshot=chat_show_screenshot)

        CLOSE_COLLECTION_BUTTON = self.get_close_collection_button_position()
        x = CLOSE_COLLECTION_BUTTON['center']['x']
        y = CLOSE_COLLECTION_BUTTON['center']['y']
        await self.click(x, y, TYPE=CLOSE_COLLECTION_BUTTON['type'])
    
    
    async def close_chat_if_open(self, show_screenshot=False, show_match=False):
        img_res = await self.isChatOpen(show_match=show_match, show_screenshot=show_screenshot)
        print(f"Chat is open: {img_res}")
        chatIsOpen = img_res['found']
        chatButton = img_res['match']['coordinates']
        if chatIsOpen:
            print("Chat is open, closing...")
            await self.click(chatButton['center']['x'], chatButton['center']['y'], TYPE='absolute')

        else:
            print("Chat is closed.")
            
            
    async def align_character_south_west(self, duration=3):
        # TODO(adrian): i dont like this. move this to System.py
        import pydirectinput
        
        # press S and A, at the same time
        pydirectinput.keyDown('a')
        pydirectinput.keyDown('s')

        # waits duration of keypress
        await asyncio.sleep(duration)

        # un-presses
        pydirectinput.keyUp('a')
        pydirectinput.keyUp('s')
        
#singleton        
Roblox = Roblox()
