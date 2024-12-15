import sys
import os
import asyncio

# delete these imports below, only for testing the shitty mouse events
import time
import pyautogui
import pydirectinput
import keyboard

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from lib.configuration import CONFIGURATION
from lib.biome import Biome
from lib.discord import Discord
from lib.roblox import Roblox
from lib.system import System

# Função principal que roda o programa
async def server_roll():
    # fail check: unknown Biome
    # fail check: reconnect 
        
    # increment server roll number (iterations)

    # -------------------- from here
    print(f"Joining server")
    await Roblox.join_private_server(force=True) # reopens game, joins pvt, brings to foreground and maximizes
    
    await asyncio.sleep(4) # waits 4 seconds, because no one insta-joins anyway.
    await Roblox.wait_server() # for "Waiting for available server..." msg, that can take a while. NOTE: If Roblox takes too long to load, this will falsely pass through
    
    # TODO(adrian): check if fetching data screen
    
    # clicks automatically once found
    # TODO(adrian): sharpen OCR. its taking about 9 tries to find
    await Roblox.wait_play_button(click_when_found=True, show_screenshot=False) # make an "use_image_match" flag, to use image matching instead of OCR
    
    
    # FLAG-ify this 
    await Roblox.click_auto_roll_button() # toggle auto roll
    await Roblox.click_skip_aura_button() # only do this if you did auto roll too?????? or maybe just blind click this every time
    
    # both will check for chat before actually clicking the element
    # TODO(adrian): validate this wont fail
    await Roblox.click_side_menu_button_position(2, check_for_chat=True, chat_show_screenshot=False)
    await Roblox.click_close_collection_button(check_for_chat=True, chat_show_screenshot=False)
    
    # hold a+s for alignment
    await Roblox.align_character_south_west() # moves A+S for 3 seconds then stop (might change this)
    
    
    print(f"Server I: Detecting Biome...")
    # Biome_result = await Biomes.handleBiome();
    # fuck me. this will be annoying to do.
    # handle Biome detection
    
    # statistics
    
    # repeat
    pass
    
async def test_server_roll():
    # fail check: unknown Biome
    # fail check: reconnect 
        
    # increment server roll number (iterations)

    # -------------------- from here
    print(f"Joining server")
    await Roblox.join_private_server(force=True) # reopens game, joins pvt, brings to foreground and maximizes
    
    await asyncio.sleep(4) # waits 4 seconds, because no one insta-joins anyway.
    
    # // UPDATE: no.
    # await Roblox.wait_server() # for "Waiting for available server..." msg, that can take a while. NOTE: If Roblox takes too long to load, this will falsely pass through
    
    # // UPDATE: no.
    # # TODO(adrian): check if fetching data screen
    
    # # clicks automatically once found
    # # TODO(adrian): sharpen OCR. its taking about 9 tries to find
    await Roblox.wait_play_button(click_when_found=True, show_screenshot=False) # make an "use_image_match" flag, to use image matching instead of OCR
    
    
    # # FLAG-ify this 
    # await Roblox.click_auto_roll_button() # toggle auto roll
    # await Roblox.click_skip_aura_button() # only do this if you did auto roll too?????? or maybe just blind click this every time
    
    # # both will check for chat before actually clicking the element
    # # TODO(adrian): validate this wont fail
    # await Roblox.click_side_menu_button_position(2, check_for_chat=True, chat_show_screenshot=False)
    # await Roblox.click_close_collection_button(check_for_chat=True, chat_show_screenshot=False)
    
    # # hold a+s for alignment
    # await Roblox.align_character_south_west() # moves A+S for 3 seconds then stop (might change this)
    
    
    # print(f"Server I: Detecting Biome...")
    # # Biome_result = await Biomes.handleBiome();
    # # fuck me. this will be annoying to do.
    # # handle Biome detection
    
    # # statistics
    
    # # repeat
    pass
        
        
async def main():
    # >> biome checking development
    # await Biome.handle_biome()

    # >> server roll func development
    # await server_roll()
    # await discord.Message({'embed': True, 'text': 'teste'}).Send()
    
    await test_server_roll()
    
    pass
    

if __name__ == "__main__":
    try: 
        System.event_loop.run_until_complete(main())
    except asyncio.CancelledError:
        print("Program finished by user request.")