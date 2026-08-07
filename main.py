import asyncio
import aiohttp
import os

# Load token from environment variable
TOKEN = os.environ.get("DISCORD_TOKEN", "YOUR_USER_TOKEN_HERE")
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
            print(f"Server Name: {guild.get('name')} | ID: {guild.get('id')}")

asyncio.run(main())
