import random
import unittest
import itertools


class MasterMind:
    def __init__(self, cli):

        # Green, Red, Yellow, Orange, Purple, Blue
        self.colors = ['G', 'R', 'Y', 'O', 'P', 'B']

        random.shuffle(self.colors)
        self.board = self.colors[:4]
        self.history = []
        self.cli = cli

    def reset(self):
        random.shuffle(self.colors)
        self.board = self.colors[:4]
        self.history.clear()

    # Process guess
    def guess(self, guess):
        if len(guess) != 4:
            raise Exception("Guess must be 4 chars long.")
        for l in guess:
            if l not in self.colors:
                raise Exception("{} is not an option.".format(l))
        red, white = self._check(guess)
        self.history.append({
            'guess': guess,
            'red': red,
            'white': white,
            'total': red + white
        })
        if self.cli:
            self._print()
        return red, white

    # Print all the history
    def _print(self):
        for line in self.history:
            print('r={} w={} g={}'.format(line['red'], line['white'], line['guess']))

    # Check a guess
    def _check(self, guess):
        red = 0
        white = 0
        for i, item in enumerate(guess):
            if self.board[i] == item:
                red += 1
            elif item in self.board:
                white += 1
        return red, white 


class AI:
    def __init__(self, mastermind):
        self.mastermind = mastermind

        # A list of data objects, each containing an options key and an amount key
        # The options key contains a list of colors, and the amount key how many of
        # those are in the solution. These are made by looking at the difference
        # between two guesses.
        self.color_find_data = []

    # Make a guess
    def make_guess(self):
        certain_yes, certain_no = self.process_color_data()
        if len(certain_no) == 2:
            colors = list(set(self.mastermind.colors) - certain_no)
        else:
            colors = list(certain_yes)
        open_options = list(set(self.mastermind.colors) - certain_yes - certain_no)
        colors.extend(open_options)
        combinations = itertools.permutations(colors, 4)
        for combination in combinations:
            if self.check_guess(combination):
                return "".join(combination)
        raise Exception("No combination is possible")

    def check_guess(self, guess):
        for history_item in self.mastermind.history:
            if "".join(guess) == history_item['guess']:
                return False
            if history_item['red'] == 0:
                for i in range(0, 4):
                    if history_item['guess'][i] == guess[i]:
                        return False
        return True            

    # Find color_find_data between two guesses. 
    def find_info(self, result_1, result_2):
        total_diff = result_1['total'] - result_2['total']
        if total_diff != 0:
            only_in_1, only_in_2 = self.diff(result_1['guess'], result_2['guess'])
            more, less = (only_in_1, only_in_2) if total_diff > 0 else (only_in_2, only_in_1)
            self.color_find_data.append({
                'options': only_in_1,
                'amount': result_1['total'] - result_2['total']
            })
            self.color_find_data.append({
                'options': only_in_2,
                'amount': result_2['total'] - result_1['total']
            })

    # Process the stored information
    def process_color_data(self):
        # Shortcut if all colors were known in the last guess
        if len(self.mastermind.history) != 0:
            last_history = self.mastermind.history[-1]
            if last_history['red'] + last_history['white'] == 4:
                return set(last_history['guess']), set(self.mastermind.colors) - set(last_history['guess'])
        certain_yes = set()
        certain_no = set()
        for item in self.color_find_data:
            # If there is one more correct color, and only one option
            # that color has to be in the solution.
            if item['amount'] == 1 and len(item['options']) == 1:
                certain_yes.add(item['options'][0])
            # if there is one less correct color, and only one option
            # that color has to not be be in the solution.
            elif item['amount'] == -1 and len(item['options']) == 1:
                certain_no.add(item['options'][0])
        return certain_yes, certain_no

    # Find the diff between two guesses              
    def diff(self, result_1, result_2):
        only_in_1 = [c for c in result_1 if c not in result_2]
        only_in_2 = [c for c in result_2 if c not in result_1]
        return only_in_1, only_in_2 

    def solve(self):
        done = False
        while not done:
            r, w = self.mastermind.guess(self.make_guess())
            try:
                self.find_info(self.mastermind.history[-2], self.mastermind.history[-1])
            except IndexError:
                pass
            self.process_color_data()
            if r == 4:
                done = True
            

class TestAI(unittest.TestCase):
    def setUp(self):
        self.m = MasterMind(False)
        self.m.board = ['G', 'R', 'B', 'Y']
        self.ai = AI(self.m)

    def test_diff(self):
       result = self.ai.diff('GRBY', 'GRBO')
       self.assertEqual(result, (['Y'], ['O']))

    def test_color_find_data(self):
        self.ai.find_info({'guess': 'GRBY', 'total': 2}, {'guess': 'GRBO', 'total': 3})
        self.assertEqual(self.ai.color_find_data[0], {'options': ['Y'], 'amount': -1})
        self.assertEqual(self.ai.color_find_data[1], {'options': ['O'], 'amount': 1})

def test_ai():
    games = []
    m = MasterMind(False)
    for i in range(0, 100000):
        if i % 1000 == 0:
            print(i)
        m.reset()
        ai = AI(m)
        ai.solve()
        games.append(len(m.history))
    print('Average tries: {}'.format(sum(games)/len(games)))

if __name__ == '__main__':
    test_ai()
