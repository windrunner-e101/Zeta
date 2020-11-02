import discord
from discord.ext import commands
from discord.utils import get


class UtilCmds(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # noinspection PyBroadException
    @commands.command()
    async def role(self, ctx, role: str):

        # role ids mapped to relevant keys in a dict because I don't have a database
        self_role_map = {
            'python': 768399999150063657,
            'js': 768400144327901205,
            'c++': 768400048501030933,
            'cpp': 768400048501030933,
            'c': 768400211872579595
        }

        # Attempt to get a role object relevant to the argument the user provided using the get() function, if
        # successful, assign that role to message author. Best way to make sure users don't be getting roles they're not
        # supposed to like admin, as admin isn't in the dict
        try:
            role_obj = get(ctx.guild.roles, id=self_role_map[role.lower()])

            if role_obj in ctx.author.roles:
                await ctx.author.remove_roles(role_obj)
                embed = discord.Embed(title=f"{ctx.author}", description=f'Removed role `{role_obj.name}`',
                                      color=discord.Colour.red())
            else:
                await ctx.author.add_roles(role_obj)
                embed = discord.Embed(title=f"{ctx.author}", description=f'Gave you role `{role_obj.name}`',
                                      color=discord.Colour.blue())

            await ctx.send(embed=embed)

        # hopefully the only exception that can occur is this.
        except Exception:
            await ctx.send(
                "That role does not exist or I cannot give it to you, use `.role` without any argument to get a list "
                "of user assignable roles")

    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed(title="Pong!",
                              description=f"The message round trip took {round(self.bot.latency * 1000)}ms",
                              color=discord.Color.dark_orange())
        await ctx.send(embed=embed)

    # Error handler of role command, returns a list of self assignable roles if no argument is passed after using .role
    @role.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="Self assignable roles", description="Python\nJS\nC++\nC",
                                  color=discord.Colour.gold())
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(UtilCmds(bot))
