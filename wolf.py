import discord
import asyncio
import random
from roles import*
from vote import*

class Player():
    def __init__(self,member):
        self.member = member
        self.role = None#the role of that the player has in the game
        self.guildRole = 'None'#the role that the player has in the game, either alive or dead, specs
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
        global Roles
        self.creator = None
        self.participants = []
        self.alives = []
        self.dead = []
        self.spectator = []
        self.guild = Guild
        self.channels = []
        self.roles = [Wolf(self),Villager(self)]
        self.temp = None
        self.entry = None
        self.turn = 0
        self.time = 0
        self.state = 'created'
        self.guildRoles = []
        self.guildRoles.append(Guild.get_role(722171265372258378))#getting the alive role
        self.guildRoles.append(Guild.get_role(722171307034148972))#getting the dead role
        self.guildRoles.append(Guild.get_role(722171324293841020))#getting the spec role
        overwrite = {self.guild.default_role:discord.PermissionOverwrite(read_messages = False)}
        self.gameCategory = await self.guild.create_category(creator.display_name+"'s Game",overwrites = overwrite)#nGame will be increamented before

    def getUser(self,id):
        for participant in self.participants:
            if participant.member.id == id:
                return participant

    async def deleteGame(self):
        for channel in self.channels:
            await channel.delete()
        await self.gameCategory.delete()
        await self.entry.delete()
        for member in self.spectator:
            await member.remove_roles(self.guildRoles[2])

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
        await participant.member.add_roles(self.guildRoles[0])
        participant.guildRole = 'alive'

    async def addSpectator(self,member):
        await self.channels[0].set_permissions(member,read_messages = True,send_messages = False)
        await member.add_roles(self.guildRoles[2])
        self.spectator.append(member)

    async def removePeople(self,player):#here player is not from Player class but discord.member class
        for role in self.guildRoles:
            try:
                await player.remove_roles(role)
            except:
                pass
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

    async def giveRoles(self):
        listRoles = self.roles
        for role in listRoles:
            if role.name != 'villager':
                await self.addChannel(role.name)
                role.channel = self.channels[-1] #the last channel in the list is the channel that was created
        for participant in self.participants:
            choosed = random.choice(listRoles)
            participant.role = choosed.name
            print(participant.member.display_name + choosed.name)
            choosed.players.append(participant)
            for channel in self.channels:
                if channel.name == choosed.name:
                    await channel.set_permissions(participant.member,send_messages = True)
            #listRoles.remove(choosed)

    async def kill(self,player):#receive the player that have been killed, either by the village or during the night
        self.alives.remove(player)
        self.dead.append(player)
        await player.member.remove_roles(self.guildRoles[0])#removing the alive role from the player
        await player.member.add_roles(self.guildRoles[1])#putting the dead role to the player
        await self.gameCategory.set_permissions(player.member,send_messages = False)
        self.guildRole = 'dead'
        #await player.role.activateRole("dead")

    async def start(self):#main function of the game that coordinates all the different parts such as the calling of the day, the night, distribution of roles etc
        self.turn = 1#setting the night for the first turn of the game
        self.state = 'started'
        await self.giveRoles() #calling the function that give lg roles to the participants
        while self.state!='finished':
            await self.night()
            self.turn+=1
            await self.day()
            self.turn+=1
        #then if we reach here it means that the game has ended
        await self.channels[0].send("The game will close in 1 minute")
        await asyncio.wait(60)
        await deleteGame(self.creator.member.id)

    async def day(self):
        '''
        if self.turn == 2:#meaning it's the first day of the game and we need to elect a mayor
            message = await self.channels[0].send("You need to elect a mayor to rule the town !\nPlease react on the emoji to sign up for mayor")
            await message.add_reaction("🤚")
            self.state = 'election'
            '''
        self.state = 'day'
        self.time = 90
        await self.channels[0].send("You have to do a vote to kill someone that you think is deadly for the village (mention the person for which you vote)")
        await self.display_vote(1)
        while self.time > 0:
            await asyncio.sleep(1)
            self.time-=1
            await self.display_vote()
        mostVoted = [self.alives[0]]
        for player in self.alives:
            print(mostVoted[0].member.display_name)
            if player.voted > mostVoted[0].voted:
                mostVoted = [player]
            elif player.voted == mostVoted[0].voted:
                mostVoted.append(player)
        if len(mostVoted) > 1:#mean that some people have an equal number of vote against them
            print("equal")
            #will call the mayor to choose who will be killed
        else:
            await self.channels[0].send("You have chosen to kill "+mostVoted[0].member.mention)
            await self.kill(mostVoted[0])

    async def night(self):
        self.state = 'night'
        for role in self.roles:
            if role.activation == self.state:
                await role.activateRole()

    async def display_vote(self,state = 0):
        text = 'Current state : '+str(self.time)+' seconds left to vote\n'
        n=0
        for alive in self.alives:
            n+=1
            if n<5:
                text+=alive.member.display_name+' '+ str(alive.voted)+' | '
            else:
                text+='\n'+alive.member.display_name+' '+ str(alive.voted)+' | '
                n=0
        if state == 0:
            await self.temp.edit(content = text)
        elif state == 1:
            self.temp = await self.channels[0].send(text)


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
                    if alive.vote != None:
                        alive.voted -= 1
                    for vote in game.alives: #getting the player that is being voted against
                        if vote.member.id == mention.id:
                            vote.voted += 1
                            alive.vote = vote
                    await message.delete()
                    return#used as a break here

    for role in game.roles:
        if role.voteOn:
            if len(message.mentions) == 1:
                mention = message.mentions[0]
                for participant in role.vote.participants:
                    if participant.member.id == message.author.id:
                        if participant.vote != None:
                            participant.voted -=1
                        for vote in role.vote.candidate:
                            if vote.member.id == mention.id:
                                vote.voted += 1
                                participant.vote = vote
                        await message.delete()
                        return

async def gameReaction(reaction,user,game):
    if game.state == 'election':
        if reaction.count == 1:
            await reaction.message.remove_reaction(reaction.emoji,user)
            return
        for participant in participants:#here will check if the user alive
            if user.id == participant.member.id:
                if not participant in game.alives:
                    await reaction.message.remove_reaction(reaction.emoji,user)
                    return
        #if he get here, it mean that the user is an alive participant of the game
        await game.addMayor(user)
        return

async def resetBot():
    spec = Guild.get_role(722171324293841020)
    alive = Guild.get_role(722171265372258378)
    dead = Guild.get_role(722171307034148972)
    for member in alive.members:
        await member.remove_roles(alive)
    for member in dead.members:
        await member.remove_roles(dead)
    for member in spec.members:
        await member.remove_roles(spec)

client = discord.Client()

@client.event
async def on_ready():
    global Guild
    print('We have logged in as {0.user}'.format(client))
    Guild = client.guilds[0]
    print(Guild.me.guild_permissions.manage_roles)

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

    if message.content == "delete game":
        if message.author.guild_permissions.administrator:
            categoryId = message.channel.category_id
            for category in Guild.categories:
                if categoryId == category.id and "Game" in category.name:
                    for channel in category.channels:
                        await channel.delete()
                    await category.delete()
                    return

    if message.content == "$reset":
        if message.author.guild_permissions.administrator:
            await resetBot()#function that reset the roles in case of bugs
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
        if game.state == 'created':
            if not inGame(user):
                await game.addPeople(user)
            else:
                await game.addSpectator(user)
        else:
            await game.addSpectator(user)

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
Roles = []


client.run('NzE5NjUxNjc3MzU5MDQ2NzE3.XueeWQ.KrJRZbLwHH3a6NfSgj4wIbJsKeA')
