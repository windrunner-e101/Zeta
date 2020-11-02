import discord
import datetime
from discord.ext import commands, tasks
from dbhand import dbmember


class fun_cmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setbd(self, ctx, *, birthday):
        try:
            # bday is the datetime object that has birthday, converts from user inputted string birthday
            bday = datetime.datetime.strptime(birthday, '%d %m %Y')
            user_object = dbmember(ctx.author)
            # set the birthday_object of user_object to user inputted value
            user_object.birthday = bday
            await user_object.update()
            embed = discord.Embed(title=f"{ctx.author}",
                                  description=f'Birthday recorded!\nYour day is on '
                                              f'{datetime.datetime.strftime(bday, "%d %B %Y")}',
                                  color=discord.Color.blue())
            await ctx.send(embed=embed)

        # TypeError exception raised when strptime() cannot convert a string to datetime object because the fomat
        # is likely incorrect, this handles that exception and sends appropriate error message
        except TypeError:
            embed = discord.Embed(title=f"Date doin a confuse",
                                  description="You gave an unknown date format, try again but this time follow the "
                                              "following format:\n "
                                              "`DD MM YYYY`\n",
                                  color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command()
    async def bday(self, ctx, target: discord.Member):
        try:
            db_target = dbmember(target)
            dob = db_target.birthday
            embed = discord.Embed(title=f'{target}',
                                  description=f"Your recorded birthday is {datetime.datetime.strftime(dob, '%d %B')} ",
                                  color=discord.Color.orange())
            await ctx.send(embed=embed)

        # TypeError exception raised when strftime() cannot convert NoneType object to datetime string
        # if dob is a NoneType object, then it means that the date of birth doesn't exist in the database
        except TypeError:
            embed = discord.Embed(title=f"Couldn't find birthday",
                                  description=f"{target} hasn't set their birthday yet, "
                                              f"\ntell them to set it using 'setbd'",
                                  color=discord.Color.red())
            await ctx.send(embed=embed)

    @tasks.loop(minutes=10)
    async def bday_check(self):
        pass
#     will work on this later


def setup(bot):
    bot.add_cog(fun_cmds(bot))
