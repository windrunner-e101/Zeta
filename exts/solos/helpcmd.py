from discord.ext import commands
import discord

# code is very poorly documented I know will get to that later

role_description = """
```
Displays a list of self assignable roles, or assigns you a specified role.

Usage: .role <rolename>

Required arguments:
<rolename> The name of the role you wish to be assigned

Additional comments: To remove a previously assigned role, use the command with same role name again.
```
"""

command_blank = """
```
role    :   Lists user assignable roles
```
"""


# hehehe you thought I would have proper comments here huh

class HelpCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, arg):
        help_map = {
            'role': role_description
        }
        try:
            help_value = help_map[arg]
            embed = discord.Embed(title=f"Command : {arg}", description=help_value, color=discord.Color.greyple())
            await ctx.send(embed=embed)

        except KeyError:
            await ctx.send(
                "Couldn't find the command you were looking for, type `.help` to get a list of usable commands")
            return

    @help.error
    async def help_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="Command List", description=command_blank, color=discord.Color.magenta())
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(HelpCmd(bot))
