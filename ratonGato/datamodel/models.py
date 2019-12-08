from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from . import tests

from enum import IntEnum
import datetime


class GameStatus(IntEnum):
    CREATED = 1
    ACTIVE = 2
    FINISHED = 3

    def get_name(i):
        switcher = {
            1: 'Created',
            2: 'Active',
            3: 'Finished',
        }
        return switcher.get(i, "Invalid status")


class Game(models.Model):
    MIN_CELL = 0
    MAX_CELL = 63

    cat_user = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='games_as_cat')
    mouse_user = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='games_as_mouse',
                                   null=True, blank=True)

    cat1 = models.IntegerField(default=0,
                               validators=[MinValueValidator(MIN_CELL),
                                           MaxValueValidator(MAX_CELL)])
    cat2 = models.IntegerField(default=2,
                               validators=[MinValueValidator(MIN_CELL),
                                           MaxValueValidator(MAX_CELL)])
    cat3 = models.IntegerField(default=4,
                               validators=[MinValueValidator(MIN_CELL),
                                           MaxValueValidator(MAX_CELL)])
    cat4 = models.IntegerField(default=6,
                               validators=[MinValueValidator(MIN_CELL),
                                           MaxValueValidator(MAX_CELL)])
    mouse = models.IntegerField(default=59,
                                validators=[MinValueValidator(MIN_CELL),
                                            MaxValueValidator(MAX_CELL)])

    cat_turn = models.BooleanField(default=True)

    status = models.IntegerField(default=GameStatus.CREATED)

    # Auxiliary function to decrease code repetition
    def get_correct_position(self, value):
        if(((value % 8) + 1) % 2) == (((value // 8) + 1) % 2):
            return True
        return False

    def save(self, *args, **kwargs):
        if(self.mouse_user and self.status == GameStatus.CREATED):
            self.status = GameStatus.ACTIVE

        variable_list = [self.cat1, self.cat2, self.cat3, self.cat4,
                         self.mouse]
        for variable in variable_list:
            if not self.get_correct_position(variable):
                # Create exception
                raise ValidationError(tests.MSG_ERROR_INVALID_CELL)

        super().save(*args, **kwargs)

    def __str__(self):
        # "(0, Active)\tCat [X] cat_user_test(0, 2, 4, 6)
        # --- Mouse [ ] mouse_user_test(59)"
        if(self.mouse_user is not None):
            if(self.cat_turn):
                mouse_part = (" --- Mouse [ ] mouse_user_test(" +
                              str(self.mouse) + ")")
            else:
                mouse_part = (" --- Mouse [X] mouse_user_test(" +
                              str(self.mouse) + ")")
        else:
            mouse_part = ""

        if(self.cat_turn):
            return ("(" + str(self.pk) + ", " +
                    GameStatus.get_name(self.status) +
                    ")\tCat [X] cat_user_test(" +
                    str(self.cat1) + ", " + str(self.cat2) +
                    ", " + str(self.cat3)+", " +
                    str(self.cat4) + ")" + mouse_part)
        else:
            return ("(" + str(self.pk) + ", " +
                    GameStatus.get_name(self.status) +
                    ")\tCat [ ] cat_user_test(" +
                    str(self.cat1) + ", " + str(self.cat2) +
                    ", " + str(self.cat3) + ", " +
                    str(self.cat4) + ")" + mouse_part)


class Move(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE,
                             related_name='moves')
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    origin = models.IntegerField(default=-1)
    target = models.IntegerField(default=-1)
    date = models.DateField(default=datetime.date.today)

    def free_space(self, target):
        if(target != self.game.cat1 and target != self.game.cat2 and
           target != self.game.cat3 and target != self.game.cat4 and
           target != self.game.mouse):
            return True

        return False

    def cat_posibilities(self, origen):
        list = []
        aux_list = [origen+7, origen+9]
        for position in aux_list:
            if(self.free_space(position)
               and Game.get_correct_position(self.game, position)
               and position >= self.game.MIN_CELL
               and position <= self.game.MAX_CELL):
                list.append(position)
        return list

    def mouse_posibilities(self, origen):
        list = []
        aux_list = [origen+7, origen+9, origen-7, origen-9]
        for position in aux_list:
            if(self.free_space(position)
               and Game.get_correct_position(self.game, position)
               and position >= self.game.MIN_CELL
               and position <= self.game.MAX_CELL):
                list.append(position)
        return list

    def finish(self):
        # If mouse gets to any of this places, it wins
        top_line = [0, 2, 4, 6]
        if self.game.mouse in top_line:
            self.game.status = GameStatus.FINISHED
            return True

        # If mouse has nowhere to move, it loses
        if(not self.mouse_posibilities(self.game.mouse)):
            self.game.status = GameStatus.FINISHED
            return True

        # If all cats are out of movements, cat player loses
        if(not self.cat_posibilities(self.game.cat1)
           and not self.cat_posibilities(self.game.cat2)
           and not self.cat_posibilities(self.game.cat3)
           and not self.cat_posibilities(self.game.cat4)):
            self.game.status = GameStatus.FINISHED
            return True

        # If mouse is above every cat, cats can't stop it from
        # getting to the top, so it automatically wins
        if(self.game.mouse < self.game.cat1 and
           self.game.mouse < self.game.cat2 and
           self.game.mouse < self.game.cat3 and
           self.game.mouse < self.game.cat4):
            self.game.status = GameStatus.FINISHED
            return True

        return False

    def save(self, *args, **kwargs):
        # You can't move if the game is not activated
        if(self.game.status != GameStatus.ACTIVE):
            raise ValidationError(tests.MSG_ERROR_MOVE)

        try:
            origen = int((self.origin))
            target = int((self.target))
        except ValueError:
            origen = self.origin
            target = self.target

        # You can't move to a no valid position
        if(origen < self.game.MIN_CELL
           or origen > self.game.MAX_CELL
           or not Game.get_correct_position(self.game, origen)):
            raise ValidationError(tests.MSG_ERROR_MOVE)

        elif(self.game.cat_user == self.player
             and self.game.cat_turn):
            if not self.cat_posibilities(origen):
                raise ValidationError(tests.MSG_ERROR_MOVE)

        elif(self.game.mouse_user == self.player
             and not self.game.cat_turn):
            if not self.mouse_posibilities(origen):
                raise ValidationError(tests.MSG_ERROR_MOVE)

        # You can only move cat pieces in cat turn
        # and mouse piece in mouse turn
        # The player moving should match with the user moving of the game
        # The origin should match a correct piece
        if(self.game.cat_turn
           and self.game.cat_user == self.player
           and target in self.cat_posibilities(origen)):
            if self.game.cat1 == origen:
                self.game.cat1 = target
            elif self.game.cat2 == origen:
                self.game.cat2 = target
            elif self.game.cat3 == origen:
                self.game.cat3 = target
            elif self.game.cat4 == origen:
                self.game.cat4 = target
            else:
                raise ValidationError(tests.MSG_ERROR_MOVE)
            self.game.cat_turn = False
            self.game.save()

        elif(not self.game.cat_turn
             and self.game.mouse_user == self.player
             and target in self.mouse_posibilities(origen)):
            if self.game.mouse == origen:
                self.game.mouse = target
            else:
                raise ValidationError(tests.MSG_ERROR_MOVE)
            self.game.cat_turn = True
            self.game.save()

        else:
            raise ValidationError(tests.MSG_ERROR_MOVE)

        self.finish()
        super().save(*args, **kwargs)


class CounterManager(models.Manager):

    def inc(self):
        try:
            c = Counter.objects.get(id=1)
            c.value += 1
        except Counter.DoesNotExist:
            c = Counter(id=1)
            c.value = 1
        super(Counter, c).save()
        return c.value

    def get_current_value(self):
        try:
            c = Counter.objects.get(id=1)
        except Counter.DoesNotExist:
            c = Counter(id=1)
        super(Counter, c).save()
        return c.value


class Counter(models.Model):
    value = models.IntegerField(default=0)
    objects = CounterManager()

    def save(self, *args, **kwargs):
        raise ValidationError(tests.MSG_ERROR_NEW_COUNTER)

    def delete(self, *args, **kwargs):
        pass
