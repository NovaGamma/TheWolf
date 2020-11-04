from vote import*

class Role():#will be inside a Player inside a Game, so have access to the game and the participant
    def __init__(self,name,team,game = None,players = [],activation = None):
        self.name = name
        self.team = team
        self.game = game
        self.players = players#will be a list of Player (can be only one, but must be in a list)
        self.activation = activation
        self.channel = None
        self.voteOn = False
        self.vote = None

class Wolf(Role):
    def __init__(self,game):
        Role.__init__(self,name = 'wolf',team = 1,game = game,activation = 'night')

    async def activateRole(self):
        #create the vote
        self.vote = vote(30,self.players,self.game.alives,self.channel,"You wake up and decide who you will eat this night")
        for player in self.players:
            await self.channel.send(player.member.mention,delete_after = 10) #message to notify the wolves, for them to know that they have to play
        self.voteOn = True
        result = await self.vote.start()
        self.voteOn = False
        if result[0] == 1:
            text = "You took too much time to decide and the day is rising, you didn't eat anyone this night"
        else:
            text = "You eat "+result[1].member.display_name
        await self.channel.send(text)

class Villager(Role):
    def __init__(self,game):
        Role.__init__(self,name = 'villager',team = 0,game = game)

    async def activateRole(self):
        pass
