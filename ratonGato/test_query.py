import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'ratonGato.settings')
django.setup()

from django.contrib.auth.models import User
from datamodel.models import Game, GameStatus, Move


if __name__ == '__main__':
    # Check if user with id=10 exists, otherwise just create it
    try:
        user1 = User.objects.get(id=10)
    except User.DoesNotExist:
        user1 = User.objects.create_user(id=10,
                                         username='Nicolas',
                                         password='123')

    # Check if user with id=11 exists, otherwise just create it
    try:
        user2 = User.objects.get(id=11)
    except User.DoesNotExist:
        user2 = User.objects.create_user(id=11,
                                         username='Martin',
                                         password='abc')

    # Create a game and assign to the user with id=10
    game = Game(cat_user=user1)
    game.full_clean()
    game.save()

    # Seach all the games with only an assigned user.
    # Show the result in on-screen
    result1 = Game.objects.filter(status=GameStatus.CREATED)
    print(result1)

    # Join the user with id=11 to the game with smaller id found
    # in the previous step, and start the game.
    # Print the found object typeGamein on-screen.
    selectedGame = result1[0]
    selectedGame.mouse_user = user2
    selectedGame.save()

    print(selectedGame)

    # In  the  selected  game,  moves  the  second
    # from  position  2  to  11.
    # Print  the modified object type Game in on-screen.
    Move.objects.create(game=selectedGame, player=user1, origin=2, target=11)
    print(selectedGame)

    # In the selected game, move the mouse from position 59 to 52.
    # Print the modified object type Game in on-screen

    Move.objects.create(game=selectedGame, player=user2, origin=59, target=52)
    print(selectedGame)
