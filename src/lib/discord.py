from discord_webhook import DiscordWebhook, DiscordEmbed
import time
import asyncio

class Discord:

    def __init__(self):
        self.debug = False,
        self.webhook_url = r'https://discord.com/api/webhooks/1295125878577041408/7o_tJvSdN56gLH6SPczKHXtxfuztB-9oIZ8Lz4Iwj8pJyeGVyxFlc3rHSKIGgbh60xRM'
        self.hook = DiscordWebhook(url=self.webhook_url)
        self.message = None
        
    def Message(self, data):
        embed = data.get('embed', True)
        text = data.get('text', False)
        color = data.get('color', False)
        title = data.get('title', False)
        link = data.get('link', False)
        description = data.get('description', False)
        timestamp = data.get('timestamp', False)
        
        if embed:
            self.message = DiscordEmbed()
            if text: self.message.set_footer(text=text)
            if color: self.message.set_color(color)
            if title: self.message.set_title(title)
            if link: self.message.set_url(link)
            if description: self.message.set_description(description)
            if timestamp: self.message.set_timestamp()
        else:
            if not text:
                raise ValueError('Discord:Message - text is required when embed is False')
            if color or title or description or timestamp or link:
                print('Discord:Message - color, title, description, timestamp and link are ignored when embed is False')
            self.message = text
        return self
    
    async def SpamPing(self, pings, amount, interval=5):
        for i in range(amount):
            try:
                await self.Message({'embed': False, 'text': pings}).Send()
            except Exception as e:
                print(f'Discord:SpamPing - Error sending message: {e}')
                
            await asyncio.sleep(interval)
            
    async def Send(self):
        if isinstance(self.message, DiscordEmbed):
            self.hook.add_embed(self.message)
        else:
            self.hook.content = self.message
            
        response = self.hook.execute()
        return response

#singleton    
Discord = Discord()
