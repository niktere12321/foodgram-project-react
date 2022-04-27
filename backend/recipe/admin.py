from django.contrib import admin

from .models import Favorite, Ingredient, IngredientInRecipe, Recipe, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class IngredientInRecipeAdmin(admin.ModelAdmin):
    autocomplete_fields = ('recipe', 'ingredient')
    list_display = ('amount',)
    list_filter = ('ingredient',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    fields = ('author', 'name', 'text', 'tags', 'image', 'cooking_time')
    list_display = (
        'pk',
        'name',
        'text',
        'image',
        'cooking_time',
        'author',
        'favorite',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'

    def in_favorite(self, obj):
        return obj.favorite.all().count()


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'color')
    search_fields = ('name',)
    list_filter = ('slug',)
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    autocomplete_fields = ('recipe',)
    list_display = ('pk', 'user', 'shopping_cart', 'favorite')
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientInRecipe, IngredientInRecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
