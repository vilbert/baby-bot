
import os
import time
import random
import emojis
import asyncio
import discord
import youtube_dl

from enum import Enum
from discord import opus
from discord.ext import commands
from discord.utils import get
from youtube_dl.utils import ExtractorError, DownloadError, UnsupportedError
from youtubesearchpython import *

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(id)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'usenetrc': True
    # 'postprocessors': [{
    #     'key': 'FFmpegExtractAudio',
    #     'preferredcodec': 'webm',
    #     'preferredquality': 'best',
    # }]
}

search_reactions = [emojis.encode(":one:"), emojis.encode(":two:"), emojis.encode(":three:"), emojis.encode(":four:"), emojis.encode(":five:")]


class YTDL:
    def __init__(self):
        self.ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
        self.download_folder = "./music_files"

        self.ytdl.params['outtmpl'] = os.path.join(
            self.download_folder, self.ytdl.params['outtmpl'])

    def ytdl(self):
        return self.ytdl


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop
        self.ytdl = YTDL().ytdl
        self.voice = None
        self.channel = None
        self.ctx = None
        self.now_playing = ""
        self.queue = []

    def _check_queue(self, error=None):
        if self.voice and self.voice.is_connected():
            self.voice.stop()
            if self.queue is not None and len(self.queue) > 0:
                self._play(self.queue.pop(0))

    def _play(self, song_url: str):
        id, title = self._extract_info(song_url=song_url, download=False)
        #
        self.voice.play(discord.FFmpegPCMAudio(f'./music_files/{id}.webm'), after=self._check_queue)
        self.voice.source = discord.PCMVolumeTransformer(self.voice.source)
        self.voice.source.volume = 0.1

        self.now_playing = title
        self.bot.loop.create_task(self.ctx.send(f'Now playing: {title}'))

    def _extract_info(self, song_url: str, download: bool):
        try:
            info = self.ytdl.extract_info(url=song_url, download=download)

            id = info.get('id', '')
            title = info.get('title', 'Untitled')

            return id, title
        except Exception as e:
            print('Could not extract information from {}\n\n{}'.format(song_url, e))

    @ commands.command(pass_context=True)
    async def join(self, ctx):
        self.ctx = ctx
        self.channel = ctx.message.author.voice.channel
        self.voice = get(self.bot.voice_clients, guild=ctx.guild)

        if self.voice and self.voice.is_connected():
            await self.voice.move_to(self.channel)
        else:
            self.voice = await self.channel.connect()
            # await self.ctx.send(f'Connecting to voice channel: {self.channel}.')
        # await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)

    @ commands.command(brief="Play audio using provided link or search results.")
    async def play(self, ctx, *, song_url: str):
        self.ctx = ctx

        if "http://" in song_url or "https://" in song_url:
            id, title = self._extract_info(song_url=song_url, download=True)

            if self.voice and self.voice.is_connected():
                if self.voice.is_playing():
                    self.queue.append(song_url)
                    await self.ctx.send(f'Queue added: {title}.')
            else:
                await self.join(ctx)
                self.queue.append(song_url)
                self._check_queue()
        else:
            videosSearch = VideosSearch(
                song_url, limit=5, language='en', region='ID')
            search_results = videosSearch.result()['result']
            results_text = ""
            for i, result in enumerate(search_results, start=1):
                result_text = str(i) + ". " + result['title'] + " (" + result['duration'] + ")"
                results_text = '\n'.join([results_text, result_text])
            msg = await self.ctx.send(f'```{results_text}```')

            for r in search_reactions:
                await msg.add_reaction(r)

            def check(reaction, user):
                return user == self.ctx.message.author and str(reaction.emoji) in search_reactions

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=12, check=check)

                await reaction.message.delete()

                if reaction.emoji == emojis.encode(":one:"):
                    song_url = search_results[0]['link']
                elif reaction.emoji == emojis.encode(":two:"):
                    song_url = search_results[1]['link']
                elif reaction.emoji == emojis.encode(":three:"):
                    song_url = search_results[2]['link']
                elif reaction.emoji == emojis.encode(":four:"):
                    song_url = search_results[3]['link']
                elif reaction.emoji == emojis.encode(":five:"):
                    song_url = search_results[4]['link']

                id, title = self._extract_info(song_url=song_url, download=True)

                if self.voice and self.voice.is_connected():
                    if self.voice.is_playing():
                        self.queue.append(song_url)
                        await self.ctx.send(f'Queue added: {title}.')
                else:
                    await self.join(ctx)
                    self.queue.append(song_url)
                    self._check_queue()
            except TimeoutError:
                await msg.delete()

    @ commands.command(brief="Clear songs in queue.")
    async def clear(self, ctx):
        self.ctx = ctx

        if self.voice and self.voice.is_connected():
            if self.queue is not None and len(self.queue) > 0:
                self.queue.clear()
                await self.ctx.send(f'Queue cleared.')
            else:
                await self.ctx.send(f'Queue empty.')
        else:
            await self.ctx.send(f'Currently not connected to any voice channels.')

    @ commands.command(brief="Stop audio player.")
    async def stop(self, ctx):
        self.ctx = ctx

        if self.voice and self.voice.is_connected():
            if self.voice.is_playing() or self.voice.is_paused():
                self.queue.clear()
                self.voice.stop()
                await self.ctx.send(f'Stopping player.')
            else:
                await self.ctx.send(f'Currently not playing any songs.')
        else:
            await self.ctx.send(f'Currently not connected to any voice channels.')

    @ commands.command(brief="Pause current song.")
    async def pause(self, ctx):
        self.ctx = ctx

        if self.voice and self.voice.is_connected():
            if self.voice.is_playing():
                self.voice.pause()
                await self.ctx.send(f'Pausing song.')
            else:
                await self.ctx.send(f'Currently not playing any songs.')
        else:
            await self.ctx.send(f'Currently not connected to any voice channel.')

    @ commands.command(brief="Resume current song.")
    async def resume(self, ctx):
        self.ctx = ctx

        if self.voice and self.voice.is_connected():
            if self.voice.is_paused():
                self.voice.play(self.voice.source)
                await self.ctx.send(f'Resuming current song.')
            else:
                await self.ctx.send(f'Currently not playing any songs.')
        else:
            await self.ctx.send(f'Currently not connected to any voice channel.')

    @ commands.command(brief="Skip current song. Use queue number to jump to song.")
    async def skip(self, ctx, index: int = None):
        self.ctx = ctx

        if self.voice and self.voice.is_connected():
            if self.voice.is_playing() or self.voice.is_paused():
                if len(self.queue) > 0:
                    if index is not None and index > 0:
                        for i, q in enumerate(self.queue, start=0):
                            if i == index:
                                break
                        self.queue = self.queue[index-1:]
                    self.voice.stop()
                    await self.ctx.send(f'Skipping song.')
                else:
                    await self.ctx.send(f'There are no more songs in queue.')
                    return
            else:
                await self.ctx.send(f'Currently not playing any songs.')
        else:
            await self.ctx.send(f'Currently not connected to any voice channel.')

    @ commands.command(brief="Disconnect from current channel.")
    async def disconnect(self, ctx):
        self.ctx = ctx

        if self.voice and self.voice.is_connected():
            await self.voice.disconnect()
            await self.ctx.send(f'Disconnecting from voice channel: {self.channel}.')
        else:
            await self.ctx.send(f'Currently not connected to any voice channel.')

    @ commands.command(brief="Set audio player volume.")
    async def volume(self, ctx, new_volume=None):
        self.ctx = ctx

        if self.voice and self.voice.is_connected():
            if self.voice.is_playing():
                if new_volume is None:
                    volume = self.voice.source.volume * 100
                    await self.ctx.send(f'Current volume: {volume}.')
                    return
                new_volume = float(new_volume)
                if 0 < new_volume <= 100.0:
                    # # VOLUME LOOP
                    # old_volume = self.voice.source.volume * 100.0
                    # if new_volume < old_volume:
                    #     step = -1
                    # else:
                    #     step = 1
                    # start = int(old_volume)
                    # end = int(new_volume) + step
                    # for volume in range(start, end, step):
                    #     self.voice.source.volume = volume / 100.0
                    #     time.sleep(0.01)
                    # # END VOLUME LOOP
                    # vol = self.voice.source.volume * 100
                    # await ctx.send(f'Setting volume to: {vol}.')
                    self.voice.source.volume = new_volume / 100
                    await self.ctx.send(f'Setting volume to: {new_volume}.')
                else:
                    await self.ctx.send('Volume must be between 1 and 100.')
            else:
                await self.ctx.send(f'Currently not playing any songs.')
        else:
            await self.ctx.send(f'Currently not connected to any voice channels.')

    @ commands.command(brief="Prints current queue.")
    async def queue(self, ctx):
        self.ctx = ctx

        if self.voice and self.voice.is_connected():
            if self.voice.is_playing():
                if self.queue is not None:
                    if len(self.queue) > 0:
                        queue_text = ""
                        for i, q in enumerate(self.queue, start=1):
                            id, title = self._extract_info(song_url=q, download=False)
                            q_text = str(i) + ". " + title
                            queue_text = '\n'.join([queue_text, q_text])
                            # Limit print to 8 entries for readability.
                            if i == 8:
                                break
                        await self.ctx.send(f'```Now Playing:\n{self.now_playing}\n\nQueue:{queue_text}```')
                    else:
                        await self.ctx.send(f'```Now Playing:\n{self.now_playing}\n\nQueue is empty.```')
                else:
                    await self.ctx.send(f'There are no more songs in queue.')
            else:
                await self.ctx.send(f'Currently not playing any songs.')
        else:
            await self.ctx.send(f'Currently not connected to any voice channels.')


def setup(bot):
    bot.add_cog(Music(bot))
