from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.db.models import Min

from datamodel import constants
# Import the models
from datamodel.models import Counter, Game, GameStatus, Move
# Import the forms
from logic.forms import SignupForm, LoginForm, MoveForm


def anonymous_required(f):
    def wrapped(request):
        if request.user.is_authenticated:
            return HttpResponseForbidden(
                errorHTTP(request,
                          exception="Action restricted to anonymous users"))
        else:
            return f(request)

    return wrapped


def errorHTTP(request, exception=None):
    context_dict = {}
    context_dict[constants.ERROR_MESSAGE_ID] = exception
    context_dict["counter_global"] = Counter.objects.inc()
    return render(request, "mouse_cat/error.html", context_dict)


# Create your views here.
def index(request):
    """
    Displays home page.

    Args:
        request (HttpRequest): Metadata about the requested page

    Returns:
        render(...) (HttpResponse): Template information

    Author:
    """
    context_dict = {"counter_global": Counter.objects.get_current_value()}
    return render(request, "mouse_cat/index.html", context_dict)


@anonymous_required
def login(request):
    """
    Displays login menu or logs the user.

    Args:
        request (HttpRequest): Metadata about the requested page

    Returns:
        render(...) (HttpResponse): Template information

    Author:
    """
    context_dict = {"user_form": LoginForm(request.POST or None),
                    "counter_global": Counter.objects.get_current_value()}
    # The request is not a HTTP POST, so display the login form.
    if request.method == 'POST' and context_dict["user_form"].is_valid():
        data = context_dict["user_form"].clean()
        username = data["username"]
        password = data["password"]

        user = authenticate(username=username, password=password)

        if user and user.is_active:
            django_login(request, user)
            request.session["counter"] = 0
            return redirect(reverse("index"))

        else:
            context_dict["user_form"].add_error("username", "Username" +
                                                "/password is not valid")

    return render(request, "mouse_cat/login.html", context_dict)


@login_required
def logout(request):
    """
    Eliminates user from the session

    Args:
        request (HttpRequest): Metadata about the requested page

    Returns:
        render(...) (HttpResponse): Template information

    Author:
    """
    django_logout(request)
    context_dict = {"counter_global": Counter.objects.get_current_value()}
    return render(request, "mouse_cat/logout.html", context_dict)


@anonymous_required
def signup(request):
    """
    Displays signup menu or registers the user in the database.

    Args:
        request (HttpRequest): Metadata about the requested page

    Returns:
        render(...) (HttpResponse): Template information

    Author:
    """
    context_dict = {"user_form": SignupForm(request.POST or None),
                    "counter_global": Counter.objects.get_current_value()}
    # The request is not a HTTP POST, so display the login form.
    if request.method == 'POST' and context_dict["user_form"].is_valid():
        data = context_dict["user_form"].clean()
        username = data['username']
        password = data['password']
        password2 = data['password2']

        if password != password2:
            context_dict["user_form"].add_error("username",
                                                "Password and Repeat " +
                                                "password are not the same")

        elif len(password) < 6:
            context_dict["user_form"].add_error("username", "(?=.*too short)" +
                                                "(?=.*at least" +
                                                " 6 characters)" +
                                                "(?=.*too common)")
        else:
            try:
                User.objects.get(username=username)
                context_dict["user_form"].add_error("username",
                                                    "A user with " +
                                                    "that username" +
                                                    " already exists" +
                                                    "Username:" + username +
                                                    "Password:" + password +
                                                    "Password 2:" + password2)
            except User.DoesNotExist:
                user = User.objects.create_user(username=username,
                                                password=password)
                user.set_password(password)

                user = authenticate(username=username, password=password)
                django_login(request, user)

                return redirect(reverse("index"))

    return render(request, "mouse_cat/signup.html", context_dict)


@login_required(login_url='login')
def create_game(request):
    """
    Creates a game.

    Args:
        request (HttpRequest): Metadata about the requested page

    Returns:
        render(...) (HttpResponse): Template information

    Author:
    """
    context_dict = {"game": Game(cat_user=request.user)}
    context_dict["game"].save()
    context_dict["counter_global"] = Counter.objects.get_current_value()
    return render(request, "mouse_cat/new_game.html", context_dict)


@login_required(login_url='login')
def join_game(request):
    """
    Joins to the CREATED game where you are not playing as cat with lower id.

    Args:
        request (HttpRequest): Metadata about the requested page

    Returns:
        render(...) (HttpResponse): Template information

    Author:
    """
    min_id = (Game.objects.
          filter(status=GameStatus.CREATED).
          exclude(cat_user=request.user).
          aggregate(Min('id')))

    if min_id['id__min']:
        result = (Game.objects.
                  filter(id=min_id['id__min']))

        if result:
            context_dict = {"game": result[0]}
            context_dict["game"].mouse_user = request.user
            context_dict["game"].save()
        else:
            context_dict = {"msg_error": "There are no available games"}

    else:
        context_dict = {"msg_error": "There are no available games"}

    context_dict["counter_global"] = Counter.objects.get_current_value()
    return render(request, "mouse_cat/join_game.html", context_dict)


@login_required(login_url='login')
def select_game(request, game_id=None):
    """
    Displays all the game or selects one.

    Args:
        request (HttpRequest): Metadata about the requested page
        game_id (int): Id of the selected game

    Returns:
        retorno (HttpResponseForbidden): Error page
        render(...) (HttpResponse): Template information

    Author: Nicolas Serrano
    """
    if game_id:
        game = Game.objects.filter(id=game_id)
        if game:
            game = game[0]
            if game.status == GameStatus.CREATED:
                game.mouse_user = request.user
                game.save()

            if (game.cat_user == request.user
                    or game.mouse_user == request.user):

                context_dict = {"move_form": MoveForm(request.POST or None)}
                request.session["game_selected"] = game_id
                context_dict["game"] = game

                board = [0 for i in range(64)]
                board[game.cat1] = 1
                board[game.cat2] = 1
                board[game.cat3] = 1
                board[game.cat4] = 1
                board[game.mouse] = -1
                context_dict["board"] = board
                context_dict["counter_globa"
                             "l"] = Counter.objects.get_current_value()
                if game.status == GameStatus.ACTIVE:
                    return render(request, "mouse_cat/game.html", context_dict)
                elif game.status == GameStatus.FINISHED:
                    request.session["replay"] = 0
                    return render(request, "mouse_cat/replay.html",
                                  context_dict)

        retorno = errorHTTP(request, "Game does not exist")
        retorno.status_code = 404
        return retorno

    if request.method == 'GET':
        context_dict = {}
        as_cat = (Game.objects.
                  filter(cat_user=request.user).
                  filter(status=GameStatus.ACTIVE))
        as_mouse = (Game.objects.
                    filter(mouse_user=request.user).
                    filter(status=GameStatus.ACTIVE))
        join = (Game.objects.
                exclude(cat_user=request.user).
                filter(status=GameStatus.CREATED))
        replay = ((Game.objects.
                   filter(cat_user=request.user).
                   filter(status=GameStatus.FINISHED))
                  | (Game.objects.
                     filter(mouse_user=request.user).
                     filter(status=GameStatus.FINISHED)))
        paginator_as_cat = Paginator(as_cat, 5)
        paginator_as_mouse = Paginator(as_mouse, 5)
        paginator_join = Paginator(join, 5)
        paginator_replay = Paginator(replay, 5)

        page_as_cat = request.GET.get('page_as_cat')
        context_dict["as_cat"] = paginator_as_cat.get_page(page_as_cat)
        page_as_mouse = request.GET.get('page_as_mouse')
        context_dict["as_mouse"] = paginator_as_mouse.get_page(page_as_mouse)
        page_join = request.GET.get('page_join')
        context_dict["join"] = paginator_join.get_page(page_join)
        page_replay = request.GET.get('page_replay')
        context_dict["replay"] = paginator_replay.get_page(page_replay)

        context_dict["counter_global"] = Counter.objects.get_current_value()

        return render(request, "mouse_cat/select_game.html", context_dict)


@login_required(login_url='login')
def show_game(request):
    """
    Shows the game stored in the session.

    Args:
        request (HttpRequest): Metadata about the requested page

    Returns:
        retorno (HttpResponseForbidden): Error page
        render(...) (HttpResponse): Template information

    Author:
    """
    game_selected = request.session.get("game_selected")
    if game_selected:
        game = Game.objects.filter(id=game_selected)
        context_dict = {"move_form": MoveForm(request.POST or None)}
        if game:
            game = game[0]
            if (game.cat_user == request.user
                    or game.mouse_user == request.user):
                context_dict["game"] = game

                board = [0 for i in range(64)]
                board[game.cat1] = 1
                board[game.cat2] = 1
                board[game.cat3] = 1
                board[game.cat4] = 1
                board[game.mouse] = -1

                context_dict["board"] = board
                context_dict["counter_globa"
                             "l"] = Counter.objects.get_current_value()

                return render(request, "mouse_cat/game.html", context_dict)

    retorno = errorHTTP(request, "No game selected")
    retorno.status_code = 404
    return retorno


@login_required(login_url='login')
def move(request):
    """
    Makes a movement.

    Args:
        request (HttpRequest): Metadata about the requested page

    Returns:
        retorno (HttpResponseForbidden): Error page
        render(...) (HttpResponse): Template information

    Author:
    """
    if request.method == 'GET':
        retorno = errorHTTP(request, "GET not allowed")
        retorno.status_code = 404
        return retorno

    context_dict = {"move_form": MoveForm(request.POST or None)}
    context_dict["counter_global"] = Counter.objects.get_current_value()
    if request.method == 'POST' and context_dict["move_form"].is_valid():

        data = context_dict["move_form"].clean()
        origin = data["origin"]
        target = data["target"]
        user = request.user

        try:
            game = Game.objects.filter(id=request.session["game_selected"])
        except KeyError:
            retorno = errorHTTP(request,
                                "Not game selected for making the move")
            retorno.status_code = 404
            return retorno

        if game:
            game = game[0]
            try:
                Move.objects.create(
                    game=game, player=user, origin=origin, target=target)
            except ValidationError:
                context_dict["move_form"].add_error("origin",
                                                    "Move not allowed")

            if (game.cat_user == request.user
                    or game.mouse_user == request.user):
                context_dict["game"] = game

                board = [0 for i in range(64)]
                board[game.cat1] = 1
                board[game.cat2] = 1
                board[game.cat3] = 1
                board[game.cat4] = 1
                board[game.mouse] = -1

                context_dict["board"] = board

                return render(request, "mouse_cat/game.html", context_dict)


@login_required(login_url='login')
def get_move(request):
    """
    Returns next or preview movement.

    Args:
        request (HttpRequest): Metadata about the requested page

    Returns:
        retorno (HttpResponseForbidden): Error page
        response_data (JsonResponse): Json with the information

    Author:
    """
    if request.method == 'GET':
        retorno = errorHTTP(request, "GET not allowed")
        retorno.status_code = 404
        return retorno

    if request.method == 'POST':
        shift = int(request.POST.get('shift'))
        game = Game.objects.filter(id=request.session["game_selected"])[0]
        movement = request.session.get("replay", 0)
        max_movements = game.moves.count() -1

        if (movement == 0 and shift == -1) and (shift == 1 and movement == max_movements):
            retorno = errorHTTP(request, "Replay not allowed")
            retorno.status_code = 404
            return retorno

        response_data = {}
        movements = Move.objects.filter(game=game)

        if shift == -1:
            # The target is the origin of our backward movement
            # and origin the target of our backward movement
            movement -= 1
            request.session["replay"] = movement

            response_data['target'] = movements[movement].origin
            response_data['origin'] = movements[movement].target
            if movement == 0:
                response_data['previous'] = False
            else:
                response_data['previous'] = True
            response_data['next'] = True

        elif shift == 1:
            response_data['target'] = movements[movement].target
            response_data['origin'] = movements[movement].origin
            if movement == max_movements:
                response_data['next'] = False
            else:
                response_data['next'] = True
            response_data['previous'] = True
            movement += 1
            request.session["replay"] = movement

        return JsonResponse(response_data)
