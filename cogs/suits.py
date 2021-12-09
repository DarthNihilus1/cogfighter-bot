import sys
sys.path.append("..")
from cogs import events
from bot_globals import *


class SuitFight(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.damages = GAG_DAMAGES
        self.suitNames = SUIT_NAMES
        self.suit = ''
        self.suitHealth = 0
        self.message = None
        self.thread = None
        self.suitMaxHealth = 0
        self.participants = []
        self.channel = cogFighter.get_channel(813541240003887142)


    def healthEmoji(self):
        ratio = self.suitHealth/self.suitMaxHealth
        print(ratio)
        if ratio > 0.75:
            return "🟢"
        elif ratio > 0.5:
            return "🟡"
        elif ratio > 0.25:
            return "🟠"
        elif ratio > 0:
            return "🔴"
        else:
            return "⚫"


    @commands.command()
    async def startFight(self, ctx, level):
        self.suit = "Cold Caller"
        self.suitMaxHealth = (int(level) + 1) * (int(level) + 2) * 3
        self.suitHealth = self.suitMaxHealth
        self.channel = await discord.ext.commands.GuildChannelConverter().convert(ctx, '813541240003887142')
        cogEmbed = discord.Embed(title=f"A {self.suit} has appeared!")
        cogEmbed.set_image(url='https://cdn.discordapp.com/attachments/917177481847521300/917177636676059146/262.png')
        cogEmbed.add_field(name="Cog HP", value=f"{self.healthEmoji()} {self.suitHealth} out of {self.suitMaxHealth}")
        self.message = await self.channel.send(embed=cogEmbed)
        self.thread = await self.message.create_thread(name=f"{self.suit}")

        await self.thread.send(f"To damage the cog, use `{PREFIX}gag`, and then the gag name.")


    @commands.command()
    async def gag(self, ctx, *, gag):
        if not db.does_user_exist(ctx.author.id):
            ctx.send(embed=embedMsg(ctx, msg="Heya! Looks like you're a new toon. Explore the bot in the other playing "
                                             "channels and gather some gags before you try to fight a cog!"))
            return

        gag = gag.title()
        if gag in GAGS:
            index = GAGS.index(gag)
        else:
            await ctx.send(embed=embedMsg(ctx, msg="Not a valid gag!"))
            return

        inventory = db.fetch_data(ctx.author.id, 'inventory')
        if inventory[index] == 0:
            await ctx.send(embed=embedMsg(ctx, msg=f"You do not have a {gag}!"))
            return
        else:
            inventory[index] -= 1
            db.set_value(ctx.author.id, 'inventory', inventory)

        self.suitHealth -= GAG_DAMAGES[index]
        await ctx.send(embed=embedMsg(ctx, msg=f"You used a {gag} and dealt {str(GAG_DAMAGES[index])} damage!"))

        if not ctx.author in self.participants:
            self.participants.append(ctx.author)

        if self.suitHealth <= 0:
            await self.thread.delete()
            self.suitHealth = 0
            players = []
            for i in self.participants:
                players.append(i.name)
            players = ", ".join(players)
            await self.channel.send(embed=discord.Embed(title=f"Cog defeated! {players} received 100 Jellybeans!"))

        newEmbed = discord.Embed(title=f"A cog {self.suit} appeared!")
        newEmbed.set_image(url='https://cdn.discordapp.com/attachments/917177481847521300/917177636676059146/262.png')
        newEmbed.add_field(name="Cog HP", value=f"{self.healthEmoji()} {self.suitHealth} out of {self.suitMaxHealth}")
        await self.message.edit(embed=newEmbed)


def setup(bot):
    bot.add_cog(SuitFight(bot))
