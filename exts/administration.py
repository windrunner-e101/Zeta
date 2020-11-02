from discord.ext import commands
import discord
from dbhand import dbchannel


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def lockignore(self, ctx, target: discord.TextChannel = None):
        if target is not None:
            dbtarget = dbchannel(target)
            if not dbtarget.is_lockdown_ignored:
                dbtarget.is_lockdown_ignored = True
                await dbtarget.update()
                embed = discord.Embed(title="Success",
                                      description=f"The channel {target.mention} will be "
                                                  f"ignored during lockdown/unlock",
                                      color=discord.Color.green())
                embed.set_footer(text=f"{ctx.author}")
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="Error!",
                                      description="This channel has already been set to `ignore` mode during lockdown",
                                      color=discord.Color.red())
                await ctx.send(embed=embed)
        else:
            await self.lockignore(ctx, ctx.channel)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def lockenforce(self, ctx, target: discord.TextChannel = None):
        if target is not None:
            dbtarget = dbchannel(target)
            if dbtarget.is_lockdown_ignored:
                dbtarget.is_lockdown_ignored = False
                await dbtarget.update()
                embed = discord.Embed(title="Success",
                                      description=f"The channel {target.mention} has been set to `enforce` mode in "
                                                  f"the event of lockdown",
                                      color=discord.Color.green())
                embed.set_footer(text=f"{ctx.author}")
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="Error!",
                                      description=f"The channel {target.mention} is already set to `enforce` mode in "
                                                  f"the event of "
                                                  "lockdown",
                                      color=discord.Color.red())
                await ctx.send(embed=embed)
        pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def levelignore(self, ctx, target: discord.TextChannel = None):
        # Will implement later
        pass


def setup(bot):
    bot.add_cog(Admin(bot))
