from django.contrib import admin

# Register your models here.
from datamodel.models import Game, Move, Counter

admin.site.register(Game)
admin.site.register(Move)
admin.site.register(Counter)
