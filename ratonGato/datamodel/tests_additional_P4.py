"""
@author: Martin Salinas and Nicolas Serrano
"""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from . import tests
from .models import Counter, Game, GameStatus, Move





class GameEndTests(tests.BaseModelTest):
    def setUp(self):
        super().setUp()

    def test1(self):
        """ The fox reachs the end"""
        game = Game(cat_user=self.users[0], mouse_user=self.users[1], cat1=59,
                    mouse=9, cat_turn=False)
        game.save()

        Move.objects.create(
                game=game, player=self.users[1], origin=9, target=0)
        self.assertEqual(game.status, GameStatus.FINISHED)

    def test2(self):
        """ The fox is trapped by the hounds """
        game = Game(cat_user=self.users[0], mouse_user=self.users[1], cat3=16,
                    cat4=11, mouse=9)
        game.save()

        Move.objects.create(
                game=game, player=self.users[0], origin=11, target=18)
        self.assertEqual(game.status, GameStatus.FINISHED)

    def test3(self):
        """ The fox can move but the hounds can't """
        game = Game(cat_user=self.users[0], mouse_user=self.users[1], cat1=57,
                    cat2=59, cat3=61, cat4=54, mouse=45)
        game.save()

        Move.objects.create(
                game=game, player=self.users[0], origin=54, target=63)
        self.assertEqual(game.status, GameStatus.FINISHED)