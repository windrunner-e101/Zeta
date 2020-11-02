import discord
from discord.ext import commands
import asyncio
import dbhand


class ModCommands(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purgebots(self, ctx, limit: int):
        # Scans <limit> number of messages in the channel it is used in, if the message is by a bot, deletes it
        await ctx.send(embed=discord.Embed(title=f'{ctx.author}',
                                           description="Purging bot messages in this channel",
                                           color=discord.Color.purple()))
        count = 0
        async with ctx.channel.typing():
            async for message in ctx.channel.history(limit=limit):
                if message.author.bot:
                    await message.delete()
                    count += 1
        if limit is not None:
            number = limit
        else:
            number = 'all'
        await ctx.send(embed=discord.Embed(title=f'{ctx.author}',
                                           description=f"Scanned `{number}` messages, found `{count}` bot messages, "
                                                       f"deleted all",
                                           color=discord.Color.red()))

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, count: int):
        # deletes <count> number of messages in the channel used, (excluding the command message itself)
        await ctx.channel.purge(limit=count + 1)
        embed = discord.Embed(title=f"{ctx.author}", description=f"Deleted {count} messages",
                              colour=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def lockdown(self, ctx):
        embed1 = discord.Embed(title="Lockdown initiated",
                               description="Warning: This command will prevent all users except admins from sending"
                                           "messages in any of the channels, do you wish to continue? (Y/N)",
                               color=discord.Color.purple())
        await ctx.send(embed=embed1)

        def check(message):
            return message.author == ctx.author

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=10)
            if msg.content == 'Y':

                # list of channel ids that won't be affected with channel lockdown, add all the management channels
                # like hidden admin channel/announcement channel etc. ids here
                ignorelist = await dbhand.get_lockdown_ignored_channel_ids()
                overwrite = discord.PermissionOverwrite()
                overwrite.send_messages = False
                role = ctx.guild.default_role
                await ctx.send(embed=discord.Embed(title=f"{ctx.author}",
                                                   description="Started server-wide lockdown process",
                                                   color=discord.Color.orange()))

                async with ctx.channel.typing():
                    for channel in ctx.guild.channels:
                        if not (channel.id in ignorelist):
                            await channel.set_permissions(role, overwrite=overwrite)
                description = "A server-wide lockdown is now in effect, all users except for the Admins will not be " \
                              "able to send messages in any of the channels until it is lifted."
            elif msg.content == 'N':
                description = "Lockdown cancelled"
            embed = discord.Embed(title=f"{ctx.author}", description=description, color=discord.Color.red())
            await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            embed2 = discord.Embed(title=f"{ctx.author}", description="Command timed out", color=discord.Color.blue())
            await ctx.send(embed=embed2)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unlock(self, ctx):
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = True
        role = ctx.guild.default_role

        # list of channel ids that won't be affected with channel unlock, add all the management channels
        # like hidden admin channel/announcement channel etc. ids here
        ignorelist = await dbhand.get_lockdown_ignored_channel_ids()
        await ctx.send(embed=discord.Embed(title=f"{ctx.author}",
                                           description="Started unlock process",
                                           color=discord.Color.orange()))
        async with ctx.channel.typing():
            for channel in ctx.guild.channels:
                if not (channel.id in ignorelist):
                    await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(title=f"{ctx.author}", description="Lockdown lifted", color=discord.Color.green())
        await ctx.send(embed=embed)

    @purgebots.error
    async def purgebots_error(self, ctx, error):
        await ctx.send(error)

    @purge.error
    async def purge_error(self, ctx, error):
        await ctx.send(error)


def setup(bot):
    bot.add_cog(ModCommands(bot))
