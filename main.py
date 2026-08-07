import asyncio
import aiohttp
import os

# Clean up the token to remove any hidden newlines, carriage returns, or spaces
raw_token = os.environ.get("DISCORD_TOKEN", "YOUR_USER_TOKEN_HERE")
TOKEN = "".join(raw_token.split())
MESSAGE_CONTENT = "Hello, IF YOURE READING THIS YOU BETTER JOIN THIS https://discord.gg/t6k7gbgBGt"

async def get_my_guilds(session):
    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    url = "https://discord.com/api/v9/users/@me/guilds"
    
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            guilds = await response.json()
            print(f"Found {len(guilds)} servers joined by the token.")
            return guilds
        else:
            print(f"Failed to fetch servers. Status: {response.status}")
            print(await response.text())
            return []

async def main():
    async with aiohttp.ClientSession() as session:
        guilds = await get_my_guilds(session)
        
        for guild in guilds:
            guild_id = guild.get("id")
            guild_name = guild.get("name")
            print(f"\n[+] Starting server: {guild_name} ({guild_id})")
            
            members = await get_guild_members(session, guild_id)
            print(f"[+] Gathered {len(members)} members. Beginning sequential dispatch...")
            
            for member in members:
                user = member.get("user")
                if not user or user.get("bot"):
                    continue
                
                user_id = user.get("id")
                
                try:
                    # Send message and handle 1-second delay safely
                    await send_dm(session, user_id)
                    await asyncio.sleep(1.0)
                except Exception as e:
                    print(f"[-] Error messaging {user_id}: {e}")
                    # Brief fallback pause if an unexpected exception pops up
                    await asyncio.sleep(2.0)
            
            print(f"[✓] Finished all members in {guild_name}. Moving to next server.")
asyncio.run(main())
