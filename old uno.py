async def uno(client, channel):

    #game = subprocess.Popen(r"C:\Users\Oberon\Documents\Code Projects\IDLE - Python\Lyra\Uno.Lines", shell=True,)
    # card = [color, num]
    #0-9: number cards, 10: skip, 11: reverse, 12: d2, 13: w, 14: wd4
    #0: red, 1: blue, 2: green, 3: yellow, 4: wild

    import random
    
    #deck generation
    global deck
    global pile
    global hands
    deck = []
    pile = []
    hands = []

    counter = 0
    max = 40

    while counter < max:
        card = [int(counter/10),  counter%10]
        #print(card)
        deck.append(card)
        if card[1] != 0:
            deck.append(card)
        counter += 1

    #print('---')

    counter = 0
    max = 24

    while counter < max:
        card = [int(counter/6), 10 + (counter%3)]
        #print(card)
        deck.append(card)
        counter += 1

    #print('---')

    counter = 0
    max = 8

    while counter < max:
        card = [4, 13 + (counter%2)]
        #print(card)
        deck.append(card)
        counter += 1


    #print('---')
    #print(deck,', Length: ', len(deck))
    #print('---')


    #shuffle function
    counter = 0
    max = 107

    while counter <= max:
        num = random.randint(counter, max)
        #print(num, ', ', counter, ', ', max)
        card = deck[num]
        deck[num] = deck[counter]
        deck[counter] = card
        counter += 1


    #print(deck,', Length: ', len(deck))
    #print('---')

    #Pre-game

    global numPlayers

    hands = []
    numPlayers = 5 # F I X L A T E R

    dealSize = 7
    counter1 = 0


    while counter1 < numPlayers:
        hand = []
        counter2 = 0
        
        while counter2 < dealSize:
            num = random.randint(0, len(deck)-1)
            hand.append(deck[num])
            del deck[num]
            counter2 += 1
        hands.append(hand)
        counter1 += 1
        counter2 = 0
        
    #print(hands, len(hands))
    #print(deck, len(deck))

    num = random.randint(0, len(deck))
    pile.append(deck[num])
    deck.remove(deck[num])

    #Game loop

    player = 0
    winner = 0
    roundCount = 1
    reverse = False
    skip = False
    while winner == 0:

        #display
        await client.send_message(channel, str("It is round " + str(roundCount) + ", player" + str(player+1) + "'s turn"))
        await client.send_message(channel, str("Top card:"))
        

        
        #input
        card = []
        playing = True
        await client.send_message(channel, "What card would you like to play?")
        while playing:
            client.wait_for_message()
            print("O") ################################ Bot isn't recieving input
            @client.event
            async def on_message(message):
                print("I: " + message)
                content = message.content.lower()
                if content[0] == "$":
                    await client.send_message(channel, "Still alive")
                if content[0:4] == "play ":
                    if content[5] == "r":
                        card.append(0)
                    elif content[5] == "b":
                        card.append(1)
                    elif content[5] == "g":
                        card.append(2)
                    elif content[5] == "y":
                        card.append(3)
                if content[6].isdigit():
                    card.append(content[6])
                elif content[6] == "s":
                    card.append(10)
                elif content[6] == "r":
                    card.append(11)
                elif content[6:7] == "d2":
                    card.append(12)
                elif content[6] == "w":
                    if content[7:8] == "d4":
                        card.append(14)
                    else:
                        card.append(13)
                else:
                    await client.send_message(channel, "That's not a card silly!")

            if card in hands[player]:
                if card[0] == pile[0] or card[1] == pile [1] or card[0] == 4:
                    playing = False
        pile.insert(hands[player].pop(card), 0)


    # card = [color, num]
    #0-9: number cards, 10: skip, 11: reverse, 12: d2, 13: w, 14: wd4
    #0: red, 1: blue, 2: green, 3: yellow, 4: wild

        #effects
        if pile[0][1] > 9:
            
            if pile[0][1] == 10:
                skip = True
                
            elif pile[0][1] == 11:
                if reverse:
                    reverse = False
                else:
                    reverse = True
                    
            elif pile[0][1] == 12:
                drawPlayer
                if reverse:
                    if player-1 < 0:
                        drawPlayer = numPlayers-1
                    else:
                        drawPlayer = player-1
                else:
                    if player+1 > numPlayers-1:
                        drawPlayer = 0
                    else:
                        drawPlayer = player+1
                        
                num = random.randint(0, len(deck)-1)
                hands[drawPlayer].append(deck[num])
                deck.remove(deck[num])

                num = random.randint(0, len(deck)-1)
                hands[drawPlayer].append(deck[num])
                deck.remove(deck[num])

            elif pile[0][1] == 14:
                drawPlayer
                if reverse:
                    if player-1 < 0:
                        drawPlayer = numPlayers-1
                    else:
                        drawPlayer = player-1
                else:
                    if player+1 > numPlayers-1:
                        drawPlayer = 0
                    else:
                        drawPlayer = player+1
                        
                num = random.randint(0, len(deck)-1)
                hands[drawPlayer].append(deck[num])
                deck.remove(deck[num])

                num = random.randint(0, len(deck)-1)
                hands[drawPlayer].append(deck[num])
                deck.remove(deck[num])

                num = random.randint(0, len(deck)-1)
                hands[drawPlayer].append(deck[num])
                deck.remove(deck[num])

                num = random.randint(0, len(deck)-1)
                hands[drawPlayer].append(deck[num])
                deck.remove(deck[num])

                
                
                
        #winconcheck
        for hand in hands:
            if len(hand) == 0:
                winner = player

        #update
        if reverse:
            player -= 1
            if player < 0:
                player = numPlayers-1
            
        else:
            player += 1
            if player > numPlayers-1:
                player = 0

        if skip:
            if reverse:
                player -= 1
            if player < 0:
                player = numPlayers-1
            
            else:
                player += 1
                if player > numPlayers-1:
                    player = 0
            skip = False
            

    #print('Player ', (winner+1), ' wins!')

