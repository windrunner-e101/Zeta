import discord
from discord.ext import commands
from discord.ext import tasks
from dbhand import dbmember
import dbhand
from math import floor, sqrt
import datetime


# The cog that will take care of giving exp, and levelling up the server members
class Levels_with_postgres(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # A simple cache that gets user ids of all members in the database, useful to quickly find out if user exists
        self.all_member_ids = dbhand.get_all_member_ids()

        # The cache that stores 10 minutes worth of changes happening to the exp/level/pause etc status of the members
        # It is a python dict, the respective user id as the keys and the respective dbmember object as the values
        self.cache = {}

        # Starting the loop that updates database every 10 minutes
        self.update_database.start()

    @commands.Cog.listener()
    async def on_message(self, message):

        # The if condition that denies levelling up to bots, will add the check for level pause here too in future
        # update
        if not message.author.bot and not isinstance(message.channel, discord.DMChannel):
            if message.author.id not in self.all_member_ids:

                # This should make clearer how the cache is implemented
                self.cache[message.author.id] = dbmember(message.author)

                self.all_member_ids = dbhand.get_all_member_ids()
            if message.author.id in self.cache:
                self.cache[message.author.id].exp += 5 * self.cache[message.author.id].boost
                old_level = self.cache[message.author.id].level

                # The formula that calculates level based off exp
                new_level = floor((25 + sqrt(625 + 100 * self.cache[message.author.id].exp)) / 50)

                # Detecting if level up happens, no need of a tasks.loop() as the event can only happen on an on_message
                # trigger
                if new_level > old_level:
                    self.cache[message.author.id].level = new_level
                    embed = discord.Embed(title=f"{message.author}",
                                          description=f'GZ on level {new_level}, {message.author.mention}',
                                          color=discord.Color.blue())
                    await message.channel.send(embed=embed)

            # Repeating same if member doesn't exist in cache
            else:
                self.cache[message.author.id] = dbmember(message.author)
                self.cache[message.author.id].exp += 5 * self.cache[message.author.id].boost
                old_level = self.cache[message.author.id].level
                new_level = floor((25 + sqrt(625 + 100 * self.cache[message.author.id].exp)) / 50)
                if new_level > old_level:
                    self.cache[message.author.id].level = new_level
                    embed = discord.Embed(title=f"{message.author}",
                                          description=f'GZ on level {new_level}, {message.author.mention}',
                                          color=discord.Color.blue())
                    await message.channel.send(embed=embed)

    # The loop that runs once every 10 minutes, permanently saving the changes made in cache to the database
    @tasks.loop(minutes=10)
    async def update_database(self):
        for key in self.cache:
            # The update() function for a dbmember object is a coroutine, must be awaited to run.
            await self.cache[key].update()
        # Clear the cache after update is done, saving memory
        self.cache = {}

        # A little confirmation message saying that update completed successfully
        print(f'Database updated on {datetime.datetime.now()}')

    # The following section has the commands relating to the level system extension.

    # Admin command to update database manually, useful when I'm planning to take down the bot to fix bugs in
    # production, basically does the same thing as the tasks.loop() update_database() but I'd typed it out manually
    # because I created this command before the loop existed as I wanted to test if the update routine was even working.
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update_db(self, ctx):
        for key in self.cache:
            await self.cache[key].update()
        await ctx.send("Database updated (hopefully)")

    # Command to fetch own or another member's level, target is the discord.Member object which points to the member
    # you wish to fetch the level of, it defaults to None if nothing supplied and shows own level through a recursive
    # call.
    @commands.command()
    async def level(self, ctx, target: discord.Member = None):
        if target is not None:
            try:
                # Assuming the target is in the cache, makes it quicker to fetch the level instead of having to query
                # the database.
                member = self.cache[target.id]
                level = member.level
                exp = member.exp
                embed = discord.Embed(title=f"{target}",
                                      description=f"You are currently at level: {level}\nWith exp: {exp}",
                                      color=discord.Color.blue())
                await ctx.send(embed=embed)
            except KeyError:
                # If target is not present in the cache, querying the database becomes essential, this block does
                # exactly that
                dbtarget = dbmember(target)
                embed = discord.Embed(title=f"{target}",
                                      description=f"You are currently at level: {dbtarget.level}\nWith exp: {dbtarget.exp}",
                                      colour=discord.Color.blue())
                await ctx.send(embed=embed)

        # The else block calls the self.level() function recursively and sets target equal to the message author
        # so own level is displayed if nothing is supplied to the target arg.
        else:
            await self.level(ctx, target=ctx.author)


# Obligatory setup function because the library requires it for this extension to be loaded up into the bot.
def setup(bot):
    bot.add_cog(Levels_with_postgres(bot))
