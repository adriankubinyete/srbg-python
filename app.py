import sys
import os
import asyncio
import keyboard

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from lib import Roblox, System
roblox = Roblox()
system = System()

# this is the main function. edit this
async def work():
    try:
        # fail check: unknown biome
        # fail check: reconnect 
        
        # increment server roll number (iterations)
        
        print(f"Joining server")
        await roblox.join_private_server(force=True) # reopens game, joins pvt, brings to foreground and maximizes
        
        await asyncio.sleep(4) # waits 4 seconds, bcuz no one insta-joins anyway. if we start monitoring before the waiting for available server screen, we get an incorrect pass
        await roblox.wait_server()
        
        # TODO(adrian): check if fetching data screen
        
        # wait for play button (and click it)
        
        # align camera
        
        # handle biome detection
        
        # statistics
        
        # repeat
        pass
    except asyncio.CancelledError:
        raise  # Reraise para garantir que o cancelamento seja propagado corretamente



# ALL of the code below is kinda dumb, but it works
# it runs the main function and listen for interrupt
# i dont know how to code this better :)

# monitors if user wants to stop the application
async def check_stop_application():
    while True:
        await asyncio.sleep(0.2)  # put some interval so we dont cook our cpu
        if keyboard.is_pressed('f1'):
            return True

async def main():
    
    # starts the main work, and also starts listening for stop key
    task_work = asyncio.create_task(work())
    listen_stop_application = asyncio.create_task(check_stop_application())
    
    # waits the first one to happen: either the work is done or the stop key is pressed
    done, pending = await asyncio.wait([task_work, listen_stop_application], return_when=asyncio.FIRST_COMPLETED)
    
    # now we have to check which one happened first
    
    # job finished first: we are done!
    if task_work in done:
        pass
        # print('--- application finished ---') # commenting this so we leave silently
        
    # stop key was pressed first: we need to cancel the work and stop the application!
    if listen_stop_application in done:
        
        # cancel all pending tasks!
        for task in pending:
            task.cancel()
            try:
                await task  # waits for task to be cancelled before cancelling the next one 
            except asyncio.CancelledError:
                pass

if __name__ == "__main__":
    asyncio.run(main())
