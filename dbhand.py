import os
import asyncio
import psycopg2
import discord
import json

with open('creds.json') as f:
    DATABASE_URL = json.load(f)['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


class dbmember:
    def __init__(self, member: discord.Member):
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM server_members WHERE id='{member.id}';")
            data = cur.fetchall()
            cur.close()
            self.id = data[0][0]
            self.username = f"{member}"
            self.level = data[0][2]
            self.exp = data[0][3]
            self.ispaused = data[0][4]
            self.boost = data[0][5]
            self.birthday = data[0][6]

        except IndexError as e:
            self.id = member.id
            self.username = f"{member}"
            self.level = 0
            self.exp = 0
            self.ispaused = False
            self.boost = 1
            self.add()

    async def update(self):
        try:
            cur = conn.cursor()
            cur.execute(f"UPDATE server_members "
                        f"SET exp = '{self.exp}',"
                        f"username = '{self.username}',"
                        f"level = '{self.level}',"
                        f"ispaused = {self.ispaused},"
                        f"boost = {self.boost}"
                        f"WHERE id = '{self.id}'")
            cur.close()
            conn.commit()
        except Exception as e:
            print(e)

    def add(self):
        try:
            cur = conn.cursor()
            cur.execute(f"INSERT INTO server_members(id, username, level, exp, ispaused, boost)"
                        f"VALUES ('{self.id}', '{self.username}', '{self.level}', '{self.exp}', '{self.ispaused}', '{self.boost}');")
            conn.commit()
        except Exception as e:
            print(e)


def get_all_member_ids():
    cur = conn.cursor()
    cur.execute("SELECT id from server_members")
    data = cur.fetchall()
    retlist = []
    for tup in data:
        retlist.append(tup[0])
    return retlist


class dbchannel:
    def __init__(self, channel: discord.TextChannel):
        channel_id = channel.id
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM server_channels WHERE id = '{channel_id}';")
        data = cur.fetchall()
        try:
            self.id = data[0][0]
            self.is_lockdown_ignored = data[0][1]
            self.is_levelling_ignored = data[0][2]
        except IndexError:
            self.id = channel_id
            self.is_lockdown_ignored = False
            self.is_levelling_ignored = False
            self.add()
        finally:
            cur.close()

    async def update(self):
        cur = conn.cursor()
        cur.execute(f"UPDATE server_channels "
                    f"SET lockic = '{self.is_lockdown_ignored}',"
                    f"levelic = '{self.is_levelling_ignored}';")
        conn.commit()

    def add(self):
        cur = conn.cursor()
        cur.execute(f"INSERT INTO server_channels (id, lockic, levelic)"
                    f"VALUES ('{self.id}', '{self.is_lockdown_ignored}', '{self.is_levelling_ignored}');")
        conn.commit()


async def get_lockdown_ignored_channel_ids():
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM server_channels WHERE lockic = '{True}'")
    raw_data = cur.fetchall()
    retlist = []
    for tup in raw_data:
        retlist.append(tup[0])
    return retlist

# woof = asyncio.run(get_lockdown_ignored_channel_ids())
# print(woof)
# mod1 = dbchannel(768337062529073152)
# print(mod1.is_levelling_ignored)
