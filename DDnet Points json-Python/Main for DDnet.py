#import requests
import asyncio
from ddapi import DDnetApi,DDPlayer



async def main():
    object = DDnetApi()
    name = "IceRam"
    user: DDPlayer = await object.player(name)
    if user is None:
        return -1
    
    print(f"{user.player} : {user.points.points}")
    print(user.player, user.points.points)
    await object.close()
    assert isinstance(user,DDPlayer) # == обк ддпл

asyncio.run(main())


#r = requests.get('https://httpbin.org/basic-auth/user/pass', auth=('user', 'pass'))
#r.status_code