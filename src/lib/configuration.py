
class Configuration:

    def __init__(self):
        
        self.general = {
            'WAIT_AFTER_DISCONNECT': 10, # 10 seconds, TODO(adrian): should implement an exponential backoff on this so we get ideal timing?
            'MAX_UNKNOWN_DETECTION': 5, # how many times ocr can fail to detect a biome before we say Biomes.HandleBiome() failed
            'MAX_UNKNOWN_FAILS': 5, # how many times Biomes.HandleBiome() can fail before stop trying
            'MAX_RECONNECTS': 5, # how many times we can try to reconnect to the game (should happen when we expect play button, for instance)
            'MAX_FAILS_UNTIL_STOP': 5, # dont remember 
            'INTERVAL_CHECK_NORMAL_BIOME_ENDED': 5, # how many seconds between each check if normal biome ended
            'DEBUG': False,
        }
        
        self.shortcuts = {
            'STOP_APPLICATION': 'ctrl+c',
            'LOG_INFO': 'ctrl+2',
            'OCR_SCREENSHOT_TEST': 'ctrl+f',
        }
        
        self.roblox = {
            "private_server_link": "https://www.roblox.com/games/15532962292/Sols-RNG-Eon1-1?privateServerLinkCode=92396730496003660286835807334839",
        }
        
        self.discord = {
            "should_spam_ping_interval": 2, # 2 seconds between pings
            "webhook_url": "https://discord.com/api/webhooks/1295125878577041408/7o_tJvSdN56gLH6SPczKHXtxfuztB-9oIZ8Lz4Iwj8pJyeGVyxFlc3rHSKIGgbh60xRM",
            "ping": ["@188851299255713792"]
        }
        
        self.biome = {
            'Glitch': {
                'should_send_private_server_link': True,
                'should_auto_pop_hp': False,
                'should_spam_ping': False,
                'should_ping': True,
                'should_notify': True,
                'should_wait_biome_duration': True,
                'category': 'biome',
                'color': '#bfff00',
                'chance': 30000,
                'duration': 164
            },

            'Null': {
                'should_send_private_server_link': False,
                'should_auto_pop_hp': False,
                'should_spam_ping': False,
                'should_ping': False,
                'should_notify': True,
                'should_wait_biome_duration': False,
                'category': 'biome',
                'color': '#838383',
                'chance': 13333,
                'duration': 99
            },

            'Corruption': {
                'should_send_private_server_link': False,
                'should_auto_pop_hp': False,
                'should_spam_ping': False,
                'should_ping': False,
                'should_notify': True,
                'should_wait_biome_duration': False,
                'category': 'biome',
                'color': '#6d32a8',
                'chance': 9000,
                'duration': 660
            },

            'Starfall': {
                'should_send_private_server_link': False,
                'should_auto_pop_hp': False,
                'should_spam_ping': False,
                'should_ping': False,
                'should_notify': True,
                'should_wait_biome_duration': False,
                'category': 'biome',
                'color': '#011ab7',
                'chance': 7500,
                'duration': 600
            },

            'Hell': {
                'should_send_private_server_link': False,
                'should_auto_pop_hp': False,
                'should_spam_ping': False,
                'should_ping': False,
                'should_notify': True,
                'should_wait_biome_duration': False,
                'category': 'biome',
                'color': '#ff4719',
                'chance': 6666,
                'duration': 660
            },

            'SandStorm': {
                'should_send_private_server_link': False,
                'should_auto_pop_hp': False,
                'should_spam_ping': False,
                'should_ping': False,
                'should_notify': True,
                'should_wait_biome_duration': False,
                'category': 'biome',
                'color': '#ffc600',
                'chance': 3000,
                'duration': 600
            },

            'Rainy': {
                'should_send_private_server_link': False,
                'should_auto_pop_hp': False,
                'should_spam_ping': False,
                'should_ping': False,
                'should_notify': True,
                'should_wait_biome_duration': False,
                'category': 'weather',
                'color': '#027cbd',
                'chance': 750,
                'duration': 120
            },

            'Snowy': {
                'should_send_private_server_link': False,
                'should_auto_pop_hp': False,
                'should_spam_ping': False,
                'should_ping': False,
                'should_notify': True,
                'should_wait_biome_duration': False,
                'category': 'weather',
                'color': '#dceff9',
                'chance': 600,
                'duration': 120
            },

            'Windy': {
                'should_send_private_server_link': False,
                'should_auto_pop_hp': False,
                'should_spam_ping': False,
                'should_ping': False,
                'should_notify': True,
                'should_wait_biome_duration': False,
                'category': 'weather',
                'color': '#9ae5ff',
                'chance': 500,
                'duration': 120
            },

            'Normal': {
                'should_send_private_server_link': False,
                'should_auto_pop_hp': False,
                'should_spam_ping': False,
                'should_ping': False,
                'should_notify': False,
                'should_wait_biome_duration': False,
                'category': 'biome',
                'color': '#ffffff',
                'chance': 0,
                'duration': 0
            },
            
            'Unknown': {
                'should_send_private_server_link': False,
                'should_auto_pop_hp': False,
                'should_spam_ping': False,
                'should_ping': False,
                'should_notify': False,
                'should_wait_biome_duration': False,
                'category': 'biome',
                'color': '#000000',
                'chance': 0,
                'duration': 0
            },
            
        }
        
    def _get_biomes_by_config(self, attribute):
        return [biome for biome, values in self.biome.items() if values.get(attribute) is True]

# singleton    
CONFIGURATION = Configuration()
