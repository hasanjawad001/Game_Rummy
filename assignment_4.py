import random
from functools import reduce
from collections import defaultdict
import numpy as np
from copy import copy
# %matplotlib inline

SUIT = ['H','S','D','C']
RANK = ['A', '2', '3', '4', '5','6','7']
RANK_VALUE = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'Q': 10, 'K': 10}


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.rank_to_val = RANK_VALUE[self.rank]

    def __str__(self):
        return f'{self.rank}{self.suit}'

    def __repr__(self):
        return f'{self.rank}{self.suit}'

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit


class Deck:
    def __init__(self, packs):
        self.packs = packs
        self.cards = []
        for pack in range(0, packs):
            for suit in SUIT:
                for rank in RANK:
                    self.cards.append(Card(rank, suit))

    def shuffle(self):
        random.shuffle(self.cards)
    def draw_card(self):
        card = self.cards[0]
        self.cards.pop(0)
        return card
class Player:
    """
        Player class to create a player object.
        eg: player = Player("player1", list(), isBot = False)
        Above declaration will be for your agent.
        All the player names should be unique or else you will get error.

    """
    def get_action_taken(self, action_type='pick', pile=[]):
        r = None
        if action_type=='pick':
            r= np.random.choice(1)
            card_pile = pile[-1]
            card_pile_rank = card_pile.rank_to_val
            card_stash_rank_list = []
            for card in self.stash:
                card_stash_rank_list.append(card.rank_to_val)
            if card_pile_rank in card_stash_rank_list:
                r = 0
                return r
            else:
                r = 1
                return r
        else: # drop
            r= np.random.choice(4)
            card_stash_rank_list = []
            for card in self.stash:
                card_stash_rank_list.append(card.rank_to_val)
            d={}
            for rank in card_stash_rank_list:
                if rank in d.keys():
                    d[rank] +=1
                else:
                    d[rank] = 1
            single_list=[]
            double_list=[]
            for k,v in d.items():
                if v==1:
                    single_list.append(k)
                else:
                    if k not in double_list:
                        double_list.append(k)
            if len(single_list) != 0:
                max = -1
                for elem in single_list:
                    if elem > max:
                        max = elem
                for i in range(4):
                    if self.stash[i].rank_to_val == max:
                        r = i
                        return r
            else:
                max = -1
                for elem in double_list:
                    if elem > max:
                        max = elem
                for i in range(4):
                    if self.stash[i].rank_to_val == max:
                        r = i
                        return r
        return r

    def __init__(self, name, stash=list(), isBot=False, points=0, conn=None):
        self.stash = stash
        self.name = name
        self.game = None
        self.isBot = isBot
        self.points = points
        self.conn = conn

    def deal_card(self, card):
        try:
            self.stash.append(card)
            if len(self.stash) > self.game.cardsLength + 1:
                raise ValueError('Cannot have cards greater than ')
        except ValueError as err:
            print(err.args)

    def drop_card(self, card):
        self.stash.remove(card)
        self.game.add_pile(card)
        return -1

    def meld(self):
        card_hash = defaultdict(list)
        for card in self.stash:
            card_hash[card.rank].append(card)
        melded_card_ranks = []
        for (card_rank, meld_cards) in card_hash.items():
            if len(meld_cards) >= 3:
                self.game.meld.append(meld_cards)  # meld_cards is a list
                melded_card_ranks.append(card_rank)  # card_rank is the rank of meld_cards cards
                for card in meld_cards:
                    self.stash.remove(card)

        for card_rank in melded_card_ranks:
            card_hash.pop(card_rank)
        return len(melded_card_ranks) > 0

    def stash_score(self):
        score = 0
        for card in self.stash:
            score += RANK_VALUE[card.rank]
        return score

    def get_info(self, debug):
        if debug:
            print(
                f'Player Name : {self.name} \n Stash Score: {self.stash_score()} \n Stash : {", ".join(str(x) for x in self.stash)}')
        card_ranks = []
        card_suits = []
        pileset = None
        pile = None
        for card in self.stash:
            card_suits.append(RANK_VALUE[card.rank])
            card_ranks.append(card.suit)
        if len(self.game.pile) > 0:
            return {"Stash Score": self.stash_score(), "CardSuit": card_suits, "CardRanks": card_ranks,
                    "PileRank": self.game.pile[-1].rank, "PileSuit": self.game.pile[-1].suit}
        return {"Stash Score": self.stash_score(), "CardSuit": card_suits, "CardRanks": card_ranks}


class RummyAgent():
    """
    Simple Rummy Environment

    Simple Rummy is a game where you need to make all the cards in your hand same before your opponent does.
    Here you are given 3 cards in your hand/stash to play.
    For the first move you have to pick a card from the deck or from the pile.
    The card in deck would be random but you can see the card from the pile.
    In the next move you will have to drop a card from your hand.
    Your goal is to collect all the cards of the same rank.
    Higher the rank of the card, the higher points you lose in the game.
    You need to keep the stash score low. Eg, if you can AH,7S,5D your strategy
    would be to either find the first pair of the card or by removing the highest
    card in the deck. You only have 20 turns to either win the same or collect low scoring card.
    You can't see other players cards or their stash scores.

    Parameters
    ====
    players: Player objects which will play the game.
    max_card_length : Number of cards each player can have
    max_turns: Number of turns in a rummy game
    """

    def __init__(self, players, max_card_length=5, max_turns=20):
        self.max_card_length = max_card_length
        self.max_turns = max_turns
        self.reset(players)

    def update_player_cards(self, players):
        for player in players:
            player = Player(player.name, list(), isBot=player.isBot, points=player.points, conn=player.conn)
            stash = []
            for i in range(self.max_card_length):
                player.stash.append(self.deck.draw_card())
            player.game = self
            self.players.append(player)
        self.pile = [self.deck.draw_card()]

    def add_pile(self, card):
        if len(self.deck.cards) == 0:
            self.deck.cards.extend(self.pile)
            self.deck.shuffle()
            self.pile = []
        self.pile.append(card)

    def pick_card(self, player, action):
        if action == 0:
            self.pick_from_pile(player)
        else:
            self.pick_from_deck(player)
        if player.meld():
            return {"reward": 10}
        else:
            return {"reward": -1}

    #             return -player.stash_score()

    def pick_from_pile(self, player):
        card = self.pile[-1]
        self.pile.pop()
        return player.stash.append(card)

    def pick_from_deck(self, player):
        return player.stash.append(self.deck.draw_card())

    def get_player(self, player_name):
        return_player = [player for player in self.players if player.name == player_name]
        if len(return_player) != 1:
            print("Invalid Player")
            return None
        else:
            return return_player[0]

    def drop_card(self, player, card):
        player.drop_card(card)
        return {"reward": -1}

    def computer_play(self, player):
        # Gets a card from deck or pile
        if random.randint(0, 1) == 1:
            self.pick_from_pile(player)
        else:
            self.pick_from_deck(player)

        # tries to meld if it can
        #         if random.randint(0,10) > 5 :
        player.meld()

        # removes a card from the stash
        if len(player.stash) != 0:
            card = player.stash[(random.randint(0, len(player.stash) - 1))]
            player.drop_card(card)

    def play(self):
        for player in self.players:
            if len(player.stash) == 0:
                return True
        if self.max_turns <= 0:
            return True
        return False

    def _update_turn(self):
        self.max_turns -= 1

    def reset(self, players, max_turns=20):
        self.players = []
        self.deck = Deck(1)
        self.deck.shuffle()
        self.meld = []
        self.pile = []
        self.max_turns = max_turns
        self.update_player_cards(players)


if __name__ == '__main__':

    ######################################### BASICS OF VALUE AND POLICY ITERATION
    gamma = 1.0
    n_states = 4
    n_actions = 2

    # value vector
    V = np.zeros(n_states).reshape((-1, 1))
    # Reward dictionary: key (action, from, to) // action wise
    R = {
        (0, 0, 0): 20,
        (0, 1, 1): 5,
        (0, 2, 2): 3,
        (0, 3, 3): 2,

        (1, 0, 1): -5,
        (1, 1, 2): -5,
        (1, 2, 3): -5,

        (-1, 3, 2): 10,
        (-1, 2, 1): 10,
        (-1, 1, 0): 10,
    }
    # transition probability: key (action, from, to) // state wise
    P = {
        (0, 0, 0): 0.5,
        (1, 0, 1): 0.5,

        (-1, 1, 0): 0.33,
        (0, 1, 1): 0.34,
        (1, 1, 2): 0.33,

        (-1, 2, 1): 0.33,
        (0, 2, 2): 0.34,
        (1, 2, 3): 0.33,

        (-1, 3, 3): 0.5,
        (0, 3, 3): 0.5,
    }

    def Rf(s, sn, a):
        if (a, s, sn) in R:
            return R[(a, s, sn)]
        return 0

    def Pf(s, sn, a):
        if (a, s, sn) in P:
            return P[(a,s,sn)]
        return 0.

    """ with no matrix"""
    def Rs(s, a):
        r = 0
        for j in range(n_states):
            if (a, s, j) in P:
                r += P[(a, s, j)] * Rf(a,s, j)
        return r

    def Pfv(s, a):
        ret = np.zeros(n_states).reshape((-1, 1))
        for j in range(n_states):
            if (a, s, j) in P:
                ret[j] = P[(a, s, j)]
        return ret

    Rmat = np.zeros((n_states, n_actions))
    Pmat = np.zeros((n_actions, n_states, n_states))

    for i in range(n_states):
        for k in range(n_actions):
            for j in range(n_states):
                if (k, i, j) in P:
                    Rmat[i, k] += P[(k, i, j)] * Rf(i, j, k)

    for k, i, j in P.keys():
        Pmat[k, i, j] = P[(k, i, j)]

    ############################################################ VALUE ITERATION 1.0 1st WAY MATRIX
    # for t in range(5):
    #     print("t=", t, "\tV = ", V.T)
    #     # Bellman
    #     newV = Rmat + gamma * np.sum(Pmat @ V, axis=2).T
    #     # print(newV)
    #     V[:] = np.max(newV, axis=1, keepdims=True)
    #
    # print("t=", t + 1, "\tV = ", V.T)

    ############################################################ VALUE ITERATION 2.0 2nd WAY NORMAL
    # gamma = 1
    # for t in range(5):
    #     print("t=", t, "\tV = ", V.T)
    #     for i in range(n_states):
    #         # Bellman
    #         V[i] = max(
    #             Rs(i, -1) + gamma * np.sum(Pfv(i, -1) * V),
    #             Rs(i, 0) + gamma * np.sum(Pfv(i, 0) * V),
    #             Rs(i, 1) + gamma * np.sum(Pfv(i, 1) * V)
    #         )
    # print("t=", t + 1, "\tV = ", V.T)

    ############################################################ POLICY ITERATION
    # n_iter = 10
    # gamma = 1.
    # V = np.zeros(n_states)
    #
    # pi = np.random.randint(-1, 2, size=n_states)
    #
    # for n in range(n_iter):
    #     print("n = ", n, "\t", pi, end="")
    #
    #     # evaluate
    #     for s in range(n_states):
    #         V[s] = Rs(s, pi[s]) + gamma * np.sum([Pf(s, sn, pi[s]) * V[sn] for sn in range(n_states)])
    #     print("\t", V)
    #
    #     # improve
    #     for s in range(n_states):
    #         pi[s] = np.argmax(
    #             [Rs(s, a) + gamma * np.sum([Pf(s, sn, a) * V[sn] for sn in range(n_states)]) for a in range(n_actions)]
    #         )

    ############################################################ TEMPORAL DIFFERENCE LEARNING
    import sys, time
    # model (problem to solve)
    # a: 0 - loop  1 - to next state
    # r:       +1                 +0      +100 when reaches 4
    #
    n_states = 26
    n_actions = 14


    def transition(s, a):
        s1 = s + a
        if s1 == 3:
            r = 1000
        else:
            r = (s - s1)**2
        return s1, r


    def pause_print():
        sys.stdout.write('\r')
        sys.stdout.write("\033[F")
        sys.stdout.flush()
        time.sleep(0.5)


    # Example TD(0) Update
    alpha = 1.0
    gamma = 0.9
    V = np.zeros(n_states)  # 4 states
    # pi = np.random.randint(n_actions, size=n_states) # (0, 2) meaning -> 0, 1

    np.set_printoptions(precision=2)
    for k in range(1):
        # if k == 1:  # on the second iteration it is taking always to next step
        #     pi = np.ones(n_states, dtype=np.int)
        # print("Policy:", pi)
        # Evaluation of the random policy
        for e in range(10):
            s = 28
            print("\r\tTraj: ", s, end=" ")
            # print("Policy:", pi)
            for step in range(100):
                if s < 10:
                    pi = np.random.randint(3-s, 8, size=n_states)
                elif s > 21:
                    pi = np.random.randint(-7, 1+28-s, size=n_states)
                else:
                    pi = np.random.randint(-7, 8, size=n_states)
                a = pi[s-3]
                s1, r1 = transition(s, a)
                V[s-3] += alpha * (r1 + gamma * V[s1-3] - V[s-3])
                s = s1
                # print(a, s, end=" ==> ")
                if s == 3:
                    break
            print("\t", V, end="\n")
            # pause_print()
        print()


    ############################################################ RUMMY GAME
    # p1 = Player('jawad', list())
    # p2 = Player('comp1', list(), isBot=True)
    # rummy = RummyAgent([p1, p2], max_card_length=3, max_turns=20)
    #
    # maxiter = 1
    # debug = True
    # for j in range(maxiter):
    #     for player in rummy.players:
    #         player.points = player.stash_score()
    #
    #     rummy.reset(rummy.players, max_turns=20)
    #     random.shuffle(rummy.players)
    #     # int i = 0
    #     if debug:
    #         print(f'**********************************\n\t\tGame Starts : {j}\n***********************************')
    #     while not rummy.play(): # play means stop
    #         rummy._update_turn()
    #         print(rummy.max_turns)
    #         for player in rummy.players:
    #             if player.isBot:
    #                 if rummy.play():
    #                     continue
    #                 if debug:
    #                     print(f'{player.name} Plays')
    #                 rummy.computer_play(player)
    #                 if debug:
    #                     player.get_info(debug)
    #                     if player.stash == 0:
    #                         print(f'{player.name} wins the round')
    #
    #             else:
    #                 if rummy.play():
    #                     continue
    #                 if debug:
    #                     print(f'{player.name} Plays')
    #                 player_info = player.get_info(debug)
    #
    #                 #TODO:1s action taken has to be changed
    #                 # action_taken = player.get_action_taken(action_type='pick', pile=rummy.pile)
    #                 action_taken = np.random.choice(1)
    #                 if debug:
    #                     print(f'Card in pile {player_info["PileSuit"]}{player_info["PileRank"]}')
    #                 result_1 = rummy.pick_card(player, action_taken) # pick and check to meld
    #                 result_1 = result_1["reward"]
    #                 #1e action taken has to be changed:end
    #                 if debug:
    #                     print(f'{player.name} takes action {action_taken}')
    #                 # player stash will have no cards if the player has melded them
    #                 # When you have picked up a card and you have drop it since the remaining cards have been melded.
    #
    #                 if len(player.stash) == 1:
    #                     rummy.drop_card(player, player.stash[0])
    #                     if debug:
    #                         print(f'{player.name} Wins the round')
    #                 elif len(player.stash) != 0:
    #                 #TODO:2s action drop
    #                     player_info = player.get_info(debug)
    #                     s = player_info['CardRanks']
    #                     # action_taken = player.get_action_taken(action_type='drop', pile=rummy.pile)
    #                     action_taken = np.random.choice(4)
    #                     card = player.stash[action_taken]
    #                     if debug:
    #                         print(f'{player.name} drops card {card}')
    #
    #                     result_1 = rummy.drop_card(player, card)
    #                     result_1 = result_1["reward"]
    #                 #2e
    #                 #                             pdb.set_trace()
    #                 else:
    #                     if debug:
    #                         print(f'{player.name} Wins the round')
    #                 if debug:
    #                     player.get_info(debug)

