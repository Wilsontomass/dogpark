# dogpark
dogpark minimax

Dogpark is a board game similar to Wingspan and a few other games.
The goal of the game is to collect some dogs and take them on walks, maximizing your
dog walking reputation to win the game. Dogpark is an imperfect knowledge game, since there are 3 pieces of information
not revealed to all players. These are:
1. Objective cards, chosen by each player at the start of the game and kept secret. Completing
an objective gives 3 or 7 REP depending on its difficulty
2. Bids. When choosing dogs, each player bids some amount of REP on a dog. These bids are hidden when made 
and revealed simultaneously
3. The dog deck itself, from which dogs are drawn in groups of 3 or 4 depending on the number of players.

I believe the game would still be quite good for a minimax algorithm, with some adjustments for the
imperfect information. A rough calculation of the number of states in the game:

there are 4 rounds, and each round has 3 phases where decisions are made. If we assume a 3 player game for simplicity,
we can do a rough calculation of the number of states:
1. Recruitment:
   2. players choose which dogs to bid on, of 3
   3. how much to bid. from 1-4
   4. in two rounds of bidding. 

For each round of bidding, a player has 12 choices, independent of the other players. After this however, the number of
states collapses to the permutations of the 3 dogs, i.e 6. Two rounds of bidding gives 36 states after each Recruitment
round

2. Selection:
   4. Players select from their available dogs that they have the resources to take on a walk, up to 8 dogs.

The number of dogs in the kennel rises from 2 to 8 across all 4 rounds. Assuming a worst case where all dogs could be
taken on a walk, the number of states per player per round is roughly:  
Round 1: 2 choose 2  
Round 2: 4 choose 3  
Round 3: 6 choose 3  
Round 4: 8 choose 3  
 

3. Walking:
   6. players make moves on the game board, where each move has 4 possibilities, and the game board has a maximum length
of 9. Im still trying to work out how many states this is.

