import asyncio

class vote():
    def __init__(self,time = 0,participants = [],candidate= [],channel = None,text = ''):
        self.time = time
        self.participants = participants #a list of Player objects
        if candidate == []:
            self.candidate = participants
        else:
            self.candidate = candidate #a list of Player objects
        self.channel = channel
        self.text = text
        self.message = None

    async def start(self):
        await self.channel.send(str(self.text))
        await self.display(1)
        while self.time > 1:
            await asyncio.sleep(1)
            self.time-=1
            await self.display()
        mostVoted = [self.candidate[0]]
        for player in self.candidate:
            print(mostVoted[0].member.display_name)
            if player.voted > mostVoted[0].voted:
                mostVoted = [player]
            elif player.voted == mostVoted[0].voted:
                mostVoted.append(player)
        if len(mostVoted) > 1:#mean that some people have an equal number of vote against them
            print("equal")
            return [1,mostVoted]#1 mean that there is a tie between some player
            #will call the mayor to choose who will be killed
        else:
            return [0,mostVoted[0]]#here 0 mean that there is no tie

    async def display(self,state = 0):
        text = 'Current state : '+str(self.time)+' seconds left to vote\n'
        n=0
        for participant in self.participants:
            n+=1
            if n<5:
                text+=participant.member.mention+' '+ str(participant.voted)+' | '
            else:
                text+='\n'+participant.member.mention+' '+ str(participant.voted)+' | '
                n=0
        if state == 0:
            await self.message.edit(content = text)
        elif state == 1:
            self.message = await self.channel.send(text)
