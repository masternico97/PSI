from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, reverse
from datamodel import constants
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


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
    return render(request, "mouse_cat/error.html", context_dict)


# Create your views here.
def index(request):
    return render(request, "mouse_cat/index.html")


@anonymous_required
def login(request):
    context_dict = {"user_form": LoginForm(request.POST or None)}
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
    django_logout(request)
    return render(request, "mouse_cat/logout.html")


@anonymous_required
def signup(request):
    context_dict = {"user_form": SignupForm(request.POST or None)}
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
                                                    " already exists")
            except User.DoesNotExist:
                user = User.objects.create_user(username=username,
                                                password=password)
                user.set_password(password)

                user = authenticate(username=username, password=password)
                django_login(request, user)

                return redirect(reverse("index"))

    return render(request, "mouse_cat/signup.html", context_dict)


def counter(request):
    # set session variable
    try:
        request.session["counter"] += 1
    except KeyError:
        request.session["counter"] = 0
        request.session["counter"] += 1

    context_dict = {"counter_session": request.session["counter"],
                    "counter_global": Counter.objects.inc()}
    return render(request, "mouse_cat/counter.html", context_dict)


@login_required(login_url='login')
def create_game(request):
    context_dict = {"game": Game(cat_user=request.user)}
    context_dict["game"].save()
    return render(request, "mouse_cat/new_game.html", context_dict)


@login_required(login_url='login')
def join_game(request):
    result = (Game.objects.
              filter(status=GameStatus.CREATED).
              exclude(cat_user=request.user).
              order_by('-id'))
    if result:
        context_dict = {"game": result[0]}
        context_dict["game"].mouse_user = request.user
        context_dict["game"].save()
    else:
        context_dict = {"msg_error": "There is no available games"}
    return render(request, "mouse_cat/join_game.html", context_dict)


@login_required(login_url='login')
def select_game(request, game_id=None):
    if game_id:
        game = Game.objects.filter(id=game_id)
        if(game):
            game = game[0]
            if((game.cat_user == request.user
                or game.mouse_user == request.user)
               and game.status == GameStatus.ACTIVE):
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

                return render(request, "mouse_cat/game.html", context_dict)
        retorno = errorHTTP(request, "Game does not exist")
        retorno.status_code = 404
        return retorno

    if request.method == 'GET':
        context_dict = {}
        context_dict["as_cat"] = (Game.objects.
                                  filter(cat_user=request.user).
                                  filter(status=GameStatus.ACTIVE))
        context_dict["as_mouse"] = (Game.objects.
                                    filter(mouse_user=request.user).
                                    filter(status=GameStatus.ACTIVE))

        return render(request, "mouse_cat/select_game.html", context_dict)


@login_required(login_url='login')
def show_game(request):
    game_selected = request.session.get("game_selected")
    if(game_selected):
        game = Game.objects.filter(id=game_selected)
        context_dict = {"move_form": MoveForm(request.POST or None)}
        if(game):
            game = game[0]
            if(game.cat_user == request.user
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

    retorno = errorHTTP(request, "No game selected")
    retorno.status_code = 404
    return retorno


@login_required(login_url='login')
def move(request):
    if request.method == 'GET':
        retorno = errorHTTP(request, "GET not allowed")
        retorno.status_code = 404
        return retorno

    context_dict = {"move_form": MoveForm(request.POST or None)}
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

        if(game):
            game = game[0]
            try:
                Move.objects.create(
                        game=game, player=user, origin=origin, target=target)
            except ValidationError:
                context_dict["move_form"].add_error("origin",
                                                    "Move not allowed")

            if(game.cat_user == request.user
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