#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.

"""Console only version of mastermind."""
from __future__ import print_function

import argparse
import json
import os
import random

from termcolor import colored


SCORES_FILE = 'high_scores.txt'

color_map = {
    'b': colored('b', 'blue'),
    'G': colored('G', 'grey'),
    'y': colored('y', 'yellow'),
    'g': colored('g', 'green'),
    'c': colored('c', 'cyan'),
    'm': colored('m', 'magenta'),
    'w': colored('w', 'white'),
    'r': colored('r', 'red'),
}


class Guess(object):

    """Keeps track of a guess and its evaluation."""

    def __init__(self, answer, black=0, white=0):
        """Initialize this guess.

        @type answer: string
        @param answer: The actual guess as a 4 character string.
        @type black: int
        @param black: Total colors that are correct but not in the right spot.
        @type white: int
        @param white: Total colors that are correct but and in the right spot.
        """
        self.answer = answer
        self.black = black
        self.white = white

    def __str__(self):
        """Return a User friendly string represntation.

        This method is used to display the running history of a user's guesses
        after each guess is made.  Each letter is also printed in the color
        that it represents to help the player more easily visualize each guess.

        @returns: string
        """
        return '{}, {}, {}, {},     W:{}, B:{}'.format(
            color_map.get(self.answer[0]), color_map.get(self.answer[1]),
            color_map.get(self.answer[2]), color_map.get(self.answer[3]),
            self.white, self.black)


class MasterMind(object):

    """Main class with game loop, scoring, guess evaluation etc."""

    all_colors = ('r', 'G', 'y', 'g', 'b', 'm', 'c', 'w')

    def __init__(self, num_colors):
        """Initialize the game.

        @type num_colors: int
        @param num_colors: How many colors may be used in creating the secret.

        """
        if num_colors < 3:
            num_colors = 3
        elif num_colors > 8:
            num_colors = 8
        self.num_colors = num_colors
        self.colors = MasterMind.all_colors[:self.num_colors]
        self.guesses = []
        self.secret = self.make_secret()
        self.game_over = False
        self.winner = False
        self.update_points()

    def play(self):
        """Main game loop."""
        print('valid colors are: {}'.format(self.colors))
        while not self.game_over:
            self.display_game()
            self.get_next_guess()
            self.evaluate_guess()
            self.update_points()

    def evaluate_guess(self):
        """Compare the most recent guess to the secret.

        The evaluation is stored along with the guess for review.
        A Check is done to see if the gave is won or lost.
        """
        guess = self.guesses[-1]
        secret = self.secret[:]
        answer = guess.answer[:]
        if answer == secret:
            self.game_over = True
            self.winner = True
            self.display_game_over()
            return
        elif self.points < 0:
            self.game_over = True
            self.display_game_over()
            return

        w = [secret[n] == answer[n] for n in range(4)]
        secret = [secret[i] for i, x in enumerate(w) if not x]
        answer = [answer[i] for i, x in enumerate(w) if not x]
        b = 0
        for g in answer:
            if g in secret:
                b += 1
                secret.remove(g)
        w = sum([1 for n in w if n])
        guess.white = w
        guess.black = b

    def display_game(self):
        """Draw a simple game board, with previous guesses."""
        print('-' * 24)
        for guess in self.guesses:
            print(guess)
        print('-' * 24)

    def display_game_over(self):
        """Let the player know whether he won or lost."""
        if self.winner:
            print(colored('You win! - {} points'.format(self.points), 'green'))
            initials = raw_input('Enter your initials:\n')
            self.save_score(initials)
        else:
            print('You lose!')

        show = raw_input('Would you like to see the high scores? [y/N]\n')
        if show == 'y':
            self.display_high_scores()

    def make_secret(self):
        """Create a random secret using colors in self.colors."""
        secret = []
        for _ in range(4):
            secret.append(random.choice(self.colors))
        return secret

    def update_points(self):
        """Calculate the score were the game to be won on this guess."""
        self.points = (10 - len(self.guesses)) * self.num_colors * 10
        if self.points <= 0:
            self.game_over = True
            self.display_game_over()

    def save_score(self, initials):
        """Write the score and initials to a file ranked highest to lowest."""
        with open(SCORES_FILE, 'r') as fd:
            try:
                scores = json.load(fd)
            except ValueError:
                scores = []

        with open(SCORES_FILE, 'w+') as fd:
            scores.append([self.points, initials])
            scores.sort(reverse=True)
            json.dump(scores, fd)

    def display_high_scores(self):
        """Open up the high scores file and display the scores and initials."""
        if not os.path.exists(SCORES_FILE):
            print('No high scores yet')
            return
        print('High Scores:')
        with open(SCORES_FILE, 'r') as fd:
            scores = json.load(fd)
            for score in scores:
                print('{}       {}'.format(score[0], score[1]))

    def get_next_guess(self):
        """Prompt the user for a guess."""
        print('For {} possible points:'.format(self.points))
        guess = raw_input('Enter your guess.\n')
        self.guesses.append(Guess([g for g in guess]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--colors', help='number of colors', default=6,
                        type=int)
    args = parser.parse_args()
    mm = MasterMind(args.colors)
    mm.play()
