import logging, discord
import re
from discord.ext import commands
from utils import config, db

import spotipy
from spotipy.oauth2 import SpotifyOAuth

config = config.config()
connection, _ = db.get_db_connection()

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=config.spotify_client_id,
        client_secret=config.spotify_client_secret,
        redirect_uri=config.spotify_redirect_url,
        scope="playlist-modify-private",
        open_browser=False
    )
)

class spotify(commands.Cog):
    def __init__(self, client):
        logging.info(f"Loaded {self.__class__.__name__.title()} module.")

        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not (message.channel.id == config.playlist_channel_id):
            return

        urls = re.findall(r"\b(https:\/\/open\.spotify\.com\/track\/[A-z0-9]{22})\b", message.content)

        if len(urls) == 0: return
        
        for url in urls:
            await self.addPick(url, message.author.id)
        connection.commit()
        
        sp.playlist_add_items(config.spotify_playlist_url, urls)
        await message.add_reaction("✅")
        

    async def addPick(self, url: str, user_id: int) -> int:
        db.execute("INSERT INTO picks(user_id, pick_url) VALUES(?, ?)", user_id, url)

async def setup(client):
    await client.add_cog(spotify(client))