import asyncio
import aiohttp
import os

# Clean up the token to remove any hidden newlines, carriage returns, or spaces
raw_token = os.environ.get("DISCORD_TOKEN", "YOUR_USER_TOKEN_HERE")
TOKEN = "".join(raw_token.split())
MESSAGE_CONTENT = "Hello, IF YOURE READING THIS YOU BETTER JOIN THIS https://discord.gg/t6k7gbgBGt"

async def get_my_guilds(session):
    headers = {
        "Authorization": str(TOKEN).strip(),
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    url = "https://discord.com/api/v9/users/@me/guilds"
    
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            guilds = await response.json()
            print(f"Found {len(guilds)} servers joined by the token.")
            return guilds
        else:
            print(f"Failed to fetch servers. Status: {response.status}")
            return []

async def get_guild_members(session, guild_id):
    headers = {
        "Authorization": str(TOKEN).strip(),
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    # Using the members search endpoint with a wildcard query to fetch users
    url = f"https://discord.com/api/v9/guilds/{guild_id}/members/search?query=&limit=1000"
    
    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            print(f"[DEBUG] Search endpoint status: {response.status}")
            if response.status == 200:
                members = await response.json()
                return members
            else:
                text = await response.text()
                print(f"[-] Search failed: {text[:150]}")
                return []
    except Exception as e:
        print(f"[-] Request error: {e}")
        return []
async def send_dm(session, user_id):
    headers = {
        "Authorization": str(TOKEN).strip(),
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    payload = {"recipient_id": user_id}
    
    try:
        # Wrap the request in a try/except to handle internet drops / timeouts
        async with session.post("https://discord.com/api/v9/users/@me/channels", headers=headers, json=payload, timeout=10) as dm_resp:
            if dm_resp.status == 200:
                dm_data = await dm_resp.json()
                channel_id = dm_data.get("id")
                
                msg_payload = {"content": MESSAGE_CONTENT}
                async with session.post(f"https://discord.com/api/v9/channels/{channel_id}/messages", headers=headers, json=msg_payload, timeout=10) as msg_resp:
                    if msg_resp.status == 200:
                        print(f"[✓] Successfully sent DM to user ID: {user_id}")
                    elif msg_resp.status == 403:
                        print(f"[!] Skipped {user_id}: DMs closed or user blocked.")
                    elif msg_resp.status == 429:
                        print(f"[!] Rate limited! Cooling down for 10 seconds...")
                        await asyncio.sleep(10.0)
                    else:
                        print(f"[!] Failed to send message to {user_id}. Status: {msg_resp.status}")
            elif dm_resp.status == 403:
                print(f"[!] Skipped {user_id}: Cannot open DM channel (Closed DMs).")
            else:
                print(f"[!] Failed to open DM channel with {user_id}. Status: {dm_resp.status}")
                
    except asyncio.TimeoutError:
        print(f"[!] Network timeout while messaging {user_id}. Skipping to next...")
    except aiohttp.ClientError as e:
        print(f"[!] Internet connection drop or client error: {e}. Retrying in 5 seconds...")
        await asyncio.sleep(5.0)

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
