import asyncio
import re
#local library
from lib.configuration import CONFIGURATION
from lib.roblox import Roblox
from lib.system import System

SIMILAR = {
    'H': 'N',
    '1': "l",
    'n': "m",
    'm': "n",
    't': "f",
    'f': "t",
    's': "S",
    'S': "s",
    'w': "W",
    'W': "w",
}

class Biome:

    def __init__(self):
        # align biome screenshot --- from what i've tested, this is not needed because i fixed the xy deviation from the screenshot definition
        self.SCREENSHOT_CURRENT_BIOME_X_ADJUSTMENT = 0
        self.SCREENSHOT_CURRENT_BIOME_Y_ADJUSTMENT = 0
        
        self.DETERMINE_BIOME_ITERATIONS = 10; # we will have 10 iterations to try to determine the current biome
        self.DETERMINE_BIOME_THRESHOLD=0.7
        pass
    

    async def screenshot_current_biome(self):
        # obtaining roblox dimensions
        ROBLOX = Roblox.window() # ROBLOX['bounds'] = x, y, width, height
        x = ROBLOX['bounds']['x']
        y = ROBLOX['bounds']['y']
        width = ROBLOX['bounds']['width']
        height = ROBLOX['bounds']['height']
        
        # defining the region to screenshot
        CURRENT_BIOME_TOP_LEFT = ( 
            x + self.SCREENSHOT_CURRENT_BIOME_X_ADJUSTMENT,  # 0:x
            (y + self.SCREENSHOT_CURRENT_BIOME_Y_ADJUSTMENT) + height - (height * 0.135) + ((height / 600) - 1) * 10 # 1:y
        )
        CURRENT_BIOME_BOTTOM_RIGHT = (
            CURRENT_BIOME_TOP_LEFT[0] + (width * 0.15), # 0:x
            CURRENT_BIOME_TOP_LEFT[1] + (height * 0.03), # 1:y
        )
        
        screenshot = System.screenshot(CURRENT_BIOME_TOP_LEFT, CURRENT_BIOME_BOTTOM_RIGHT)
        return screenshot
    
    
    '''
    this will do the actually ocr-to-biome matching.
    it goes over the existing biomes, goes on their characters
    and matches it on a cleaned ocr text. attributes a score, and returns the
    highest value one based on the said things above.
    TBH its more efficient to try to get a way to sharpen the IMAGE TO TEXT
    if you want more accuracy on results, and not this.
    '''
    def match_biomes(self, raw_text, threshold=0.7):
        SPECIAL_CASES = [
            "Glitch",
            "Unknown",
        ]
        
        # cleaning ocr text before trying to match it
        cleaned_text = re.sub(r'\s+', '', raw_text)  # spaces
        cleaned_text = re.sub(r'^[\[\(\{\|IJ]+', '', cleaned_text)  # prefixed
        cleaned_text = re.sub(r'[\]\)\}\|IJ]+$', '', cleaned_text)  # sufixes

        HIGHEST_CONFIDENCE = 0
        FOUND_BIOME = None
        
        # lets loop over the existing biomes, but ignore Glitch and Unknown (special cases)
        for biome_key in CONFIGURATION.biome.keys():
            if biome_key in SPECIAL_CASES:
                continue
            
            SCAN_INDEX = 0
            ACCURACY = 0
            
            # now lets iterate over each letter of biome's name
            for k, checking_char in enumerate(biome_key):
                
                # now lets iterate over the cleaned ocr
                for j in range(len(cleaned_text)):
                    INDEX = SCAN_INDEX + j
                    if INDEX >= len(cleaned_text):
                        break
                    
                    TARGET_CHAR = cleaned_text[INDEX]
                    
                    #lets check if its an exact match
                    if TARGET_CHAR == checking_char:
                        ACCURACY += 3 - j
                        SCAN_INDEX = INDEX + 1
                        break
                    
                    #lets check if its a similar match
                    if SIMILAR.get(TARGET_CHAR) == checking_char:
                        ACCURACY += 2.5 - j
                        SCAN_INDEX = INDEX + 1
                        break
                    
            # now lets calculate the confidence (ratio)
            RATIO = ACCURACY / (len(biome_key) * 2)
            
            if RATIO > HIGHEST_CONFIDENCE:
                HIGHEST_CONFIDENCE = RATIO
                FOUND_BIOME = biome_key
                
            if HIGHEST_CONFIDENCE < threshold:
                FOUND_BIOME = None
                
                # now lets try to verify its glitch biome
                internal_str_length = len(cleaned_text)
                numbers_removed_length = len(re.sub(r'\d', '', cleaned_text))
                glitch_check = internal_str_length - numbers_removed_length + (4 if '.' in cleaned_text else 0)
                if glitch_check >= 20:
                    print(f"PROBABLY GLITCH BIOME!")
                    FOUND_BIOME = "Glitch"

        return {
            'biome': FOUND_BIOME if FOUND_BIOME else 'Unknown',
            'confidence': HIGHEST_CONFIDENCE,
            'text_raw': raw_text,
            'text_cleaned': cleaned_text,
        }
    
    
    '''
    this will handle the mapping of a biome ocr to an actual available biome OR invalid value
    this will screenshot the biome area, read and try to match on an existing biome
    if it cant match an existing biome, it will match as "unknown"
    '''
    async def determine_current_biome(self, iterations=10, threshold=0.7):
        print('> Determining the current biome...')
        
        identified = {
            'biome': None,
            'confidence': 0,
            'text_raw': None,
            'text_cleaned': None,
        }
        # start a loop over the quantity we will try to identify the biome
        
        for i in range(iterations):
            i += 1
            # obtaining the image of the current biome
            screenshot = await self.screenshot_current_biome()
            
            # read what the image is saying, but apply filters on image before reading
            biome_ocr_result = System.ocr_from_screenshot(screenshot["image"], apply_filters=True, filter_strength=i*1.5)
            
            # check the returned text to see if it matches a valid biome
            identified = self.match_biomes(biome_ocr_result, threshold=threshold)
            
            print(f"> Determine #{i} : {identified['biome']} ({identified['confidence']}) [\"{identified['text_cleaned']}\"]")

            # we got something, no need to loop things over!            
            if identified['biome'] != "Unknown": break

        return identified
            
            
    '''
    waits until an actually useful biome shows up (no normal or unknowns)
    you can make the app fail on max unknowns here
    '''
    async def detect_until_interesting_biome(self):
        print(f"### Detecting biome until someting interesting is found...")
        # an interesting biome is anything that IS NOT a fail (unknown) OR normal biome.
        detected = None
        MAX_UNKNOWN_COUNT = 2
        UNKNOWN_COUNT = 0
        
        MAX_NORMAL_COUNT = 9999999 # not really relevant, just an arbitrary number
        NORMAL_COUNT = 0
        
        DETECTION_INTERVAL = 1000 # 1 milis before every biome read
        DETERMINE_INTERVAL = 500 # 500 milis before trying to determine the biome
        
        i = 0
        while True:
            i += 1
            
            print(f"### Detecting #{i}...")
            await asyncio.sleep(DETECTION_INTERVAL / 1000)
            detected = await self.determine_current_biome()
            
            print(f"### Detected biome: {detected['biome']}")
            
            if detected['biome'] not in ['Unknown', 'Normal']: # got something!
                break
            
            if detected['biome'] == "Unknown": # couldnt detect / didnt ocr properly.
                UNKNOWN_COUNT += 1
                continue
            
            if detected['biome'] == "Normal": # its just normal biome. try again
                NORMAL_COUNT += 1
                continue
            
            print(f"test!")
                
        return detected
      
    '''
    this is the general handle for biome
    it should wait for a biome, and then do things based on the found biome (notify and or spam discord, send link, etc)
    basically things that should happen once you find X biome
    '''      
    # this will handle all the biome shenanigans (notification to discord, discovering what is the current biome etc)
    async def handle_biome(self):
        interesting = await self.detect_until_interesting_biome()
        print('--- Interesting found: ', interesting)
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # async def handle_biome(self):
    #     INTERVAL_CHECK_NORMAL_BIOME_ENDED = 10 # change this to config
    #     INTERVAL_CHECK_DETECTED_UNKNOWN_BIOME = 3 # interval to check again after we find an "unknown" biome
    #     DETECTED_BIOME = None
    #     UNKNOWN_BIOME_COUNT = 0
    #     MAX_UNKNOWN_BIOME_COUNT = 10 # change this to config
        
    #     while True:
    #         if UNKNOWN_BIOME_COUNT > MAX_UNKNOWN_BIOME_COUNT:
    #             print(f"Biome 'Unknown' detected more than {MAX_UNKNOWN_BIOME_COUNT} times. Switching servers...")
    #             return {
    #                 "success": False,
    #                 "detected": None,
    #             }
                
    #         DETECTED_BIOME = await self.detect_biome() # <<<<<<<<<<<<<<<<<<<<<<<<<<< long implementation
            
    #         if DETECTED_BIOME['biome'] == 'Unknown':
    #             UNKNOWN_BIOME_COUNT += 1
    #             print(f"Unknown biome detected, trying again...")
    #             await asyncio.sleep(INTERVAL_CHECK_DETECTED_UNKNOWN_BIOME)
    #         elif DETECTED_BIOME['biome'] == 'Normal':
    #             print(f"Normal biome detected, waiting {INTERVAL_CHECK_NORMAL_BIOME_ENDED} seconds before checking again...")
    #             await asyncio.sleep(INTERVAL_CHECK_NORMAL_BIOME_ENDED)
    #         else:
    #             break # its something good! we dont have to check anymore
            
    #     print(f"Biome detected: {DETECTED_BIOME['biome']}, with confidence: {DETECTED_BIOME['confidence']}")
        
    #     # after we found an interesting biome, decide what to do with it
    #     await self.discord_notification(DETECTED_BIOME['biome']) # inside here, we check if we send notifications or not # <<<<<<<<<<<<<<<<<<<<<<<<< implement (needs config)
    #     await self.wait_for_duration(DETECTED_BIOME['biome']) # inside here, we check if we wait for duration or not # <<<<<<<<<<<<<<<<<<<<<<<<<<<<< implement (needs config)
        
    #     return {
    #         "success": True,
    #         "detected": DETECTED_BIOME, # {biome, confidence}
    #     }

#singleton    
Biome = Biome()
