import discord
import asyncio

class Player():
    def __init__(self,member):
        self.member = member
        self.role = None
        self.game = None
        self.vote = None #variable that store the person for who the player is voting for
        self.voted = 0 #variable that keep the number of vote a person has against her

    async def addRole(self,role):
        self.role = role
        for channel in self.game.channels:
            if channel.name == self.role:
                await channel.set_permissions(self.member,read_messages = True)

class Game():
    def __init__(self):
        Games.append(self)

    async def createGame(self,creator):
        self.creator = None
        self.participants = []
        self.alives = []
        self.dead = []
        self.guild = Guild
        self.channels = []
        overwrite = {self.guild.default_role:discord.PermissionOverwrite(read_messages = False)}
        self.gameCategory = await self.guild.create_category(creator.display_name+"'s Game",overwrites = overwrite)#nGame will be increamented before
        self.entry = None
        self.turn = 0
        self.time = 0
        self.state = 'created'

    async def deleteGame(self):
        for channel in self.channels:
            await channel.delete()
        await self.gameCategory.delete()
        await self.entry.delete()

    async def addChannel(self,name):
        overwrite = {self.guild.default_role:discord.PermissionOverwrite(read_messages = False)}
        self.channels.append(await self.guild.create_text_channel(name,category = self.gameCategory,overwrites = overwrite))

    async def addPeople(self,member,creator = 0):
        participant = Player(member)
        participant.game = self
        if creator:
            self.creator = participant
        self.participants.append(participant)
        self.alives.append(participant)
        await self.channels[0].set_permissions(participant.member,read_messages = True)

    async def removePeople(self,player):
        for participant in self.participants:
            if player.id == participant.member.id:
                self.participants.remove(participant)
        if len(self.participants) == 0:
            await deleteGame(player.id)
            return
        if player.id == self.creator.member.id:
            self.creator = self.participants[0]
        await self.channels[0].set_permissions(player,read_messages = False)
        await self.entry.remove_reaction("✅",player)

    async def kill(self,player):#receive the player that have been killed, either by the village or during the night
        self.alives.remove(player)
        self.dead.append(player)
        await self.gameCategory.set_permissions(player,send_messages = False)
        #dont forget to activate the role at the death for hunter as example

    async def start(self):#main function of the game that coordinates all the different parts such as the calling of the day, the night, distribution of roles etc
        self.turn = 1#setting the night for the first turn of the game
        self.state = 'started'
        #await self.giveRoles() #calling the function that give roles to the participants
        while self.state!='finished':
            #await self.night()
            self.turn+=1
            await self.day()
            self.turn+=1
        #then if we reach here it means that the game has ended
        await self.channels[0].send("The game will close in 1 minute")
        await asyncio.wait(60)
        await deleteGame(self.creator.member.id)

    async def day(self):
        if self.turn == 2:#meaning it's the first day of the game and we need to elect a mayor
            message = await self.channels[0].send("You need to elect a mayor to rule the town !\nPlease react on the emoji to sign up for mayor")
            await message.add_reaction("🤚")
            self.state = 'election'
        self.state = 'day'
        self.time = 90
        await self.channels[0].send("You have to do a vote to kill someone that you think is deadly for the village (mention the person for which you vote)")
        while self.time > 1:
            await asyncio.sleep(1)
            self.time-=1
            await self.display_vote()
        mostVoted = [self.alives[0]]
        for player in self.alives:
            if player.voted > mostVoted[0]:
                for i in range(len(mostVoted)):
                    mostVoted[i] = player
            elif player.voted == mostVoted[0]:
                mostVoted.append(particpant)
        if len(mostVoted) > 1:#mean that some people have an equal number of vote against them
            pass
        else:
            await self.channels[0].send("You have chosen to kill "+mostVoted[0].member.mention)
            await self.kill(mostVoted[0])

    async def display_vote(self):
        text = 'Current state :\n'
        n=0
        for alive in self.alives:
            n+=1
            if n<5:
                text+=alive.member.display_name+' '+ str(alive.voted)+' | '
            else:
                text+='\n'+alive.member.display_name+' '+ str(alive.voted)+' | '
                n=0


    async def addMayor(self,user):
        pass

async def createGame(message):
    global Guild
    global Games
    game = Game()
    await game.createGame(message.author)
    await game.addChannel("village")
    await game.addPeople(message.author,1)
    temp = await message.channel.send("To join "+game.gameCategory.name+" please check the validation emoji")
    await temp.add_reaction("✅")
    game.entry = temp

async def deleteGame(id):#creator id:
    for i in range(len(Games)):
        if Games[i].creator.member.id ==  id:
            temp = Games[-1]
            Games[-1] = Games[i]
            Games[i] = temp
    await Games[-1].deleteGame()
    Games.pop()

def inGame(author):
    #function that will return True if the given member is already in a game and False otherwise
    for game in Games:
        for participant in game.participants:
            if author.id == participant.member.id:
                return True
    return False

async def gameMessage(message,game):#function that treat the incomming messages from games, with the message and the game it belongs to
    if message.content.startswith("Leave"):
        await game.removePeople(message.author)

    if message.content.startswith("Start Game"):
        if message.channel.id == game.channels[0].id:
            await game.start()

    if game.state == 'day':
        if len(message.mentions) == 1:
            mention = message.mentions[0]#the user corresponding to the player which is voted against
            for alive in game.alives:
                if alive.member.id == message.author.id:
                    alive.vote.voted -= 1
                    for vote in self.game.alives: #getting the player that is being voted against
                        if vote.member.id == mention.id:
                            vote.voted +=1
                            alive.vote = vote
                    await message.delete()
                    return#used as a break here


async def gameReaction(reaction,user,game):
    if game.state == 'election':
        if reaction.count == 1:
            await reaction.message.remove_reaction(reaction.emoji,user)
        else:
            await game.addMayor(user)

client = discord.Client()

@client.event
async def on_ready():
    global Guild
    print('We have logged in as {0.user}'.format(client))
    Guild = client.guilds[0]

@client.event
async def on_message(message):
    global Guild
    global time
    if message.author == client.user:
        return

    if message.content.startswith('$delete'):
        if message.author.guild_permissions.administrator:
            if message.content.startswith('$delete bot'):
                temp = message.content.split(' ')
                number = int(temp[2])
                messages = await message.channel.history(limit = number+1).flatten()
                for m in messages:
                    if m.author == client.user:
                        await m.delete()
                await message.delete()
            else:
                temp=message.content.split(' ')
                number=int(temp[1])
                messages = await message.channel.history(limit = number+1).flatten()
                for m in messages:
                    await m.delete()
        else:
            await message.delete()
        return

    for game in Games:#part that will check if the received message belong to a message sent in a game to be treated by a dedicated function
        if message.channel.category.id == game.gameCategory.id:
            await gameMessage(message,game)

    if message.content == ("Create Game") and message.channel.name == "games":
        if not inGame(message.author):
            await createGame(message)
            await message.delete()
        else:
            await message.channel.send(message.author.mention + " You're already in a game, you can't create one",delete_after = 30)
            await message.delete()

    if message.content.startswith("clock"):
        time = int(message.content.split(" ")[1])
        temp  = time
        send = await message.channel.send(str(time)+' second left')
        while time > 0:
            await asyncio.sleep(1)
            time -= 1
            await send.edit(content = str(time)+' second left')
        await send.edit(content = 'Finished !')

    if message.content == "stop":
        time = 0


@client.event
async def on_reaction_add(reaction,user):
    if user == client.user:
        return
    if reaction.message.channel.name == "games":
        game = 0
        for g in Games:
            if g.entry.id == reaction.message.id:
                game=g
        if game == 0:
            return
        if reaction.count == 1: #mean that the reaction is a new one
            await reaction.message.remove_reaction(reaction.emoji,user)
            return
        await game.addPeople(user)

    for game in Games:#part that will check if the received message belong to a message sent in a game to be treated by a dedicated function
        if reaction.message.channel.category.id == game.gameCategory.id:
            await gameReaction(reaction,user,game)

@client.event
async def on_reaction_remove(reaction,user):
    if user == client.user:
        return
    if reaction.message.channel.name == "games":
        game = 0
        for g in Games:
            if g.entry.id == reaction.message.id:
                game = g
        if game == 0:
            return
        await game.removePeople(user)

    for game in Games:#part that will check if the received message belong to a message sent in a game to be treated by a dedicated function
        if reaction.message.channel.category.id == game.gameCategory.id:
            await gameReaction(reaction,user,game)

Games = []
time = 0
