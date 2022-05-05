import django_filters
from django_filters.rest_framework import filters
from recipe.models import Ingredient, Recipe, Tag
from users.models import User


class RecipeFilter(django_filters.FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        field_name='favorite__favorite', method='filter_favorite'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='favorite__shopping_cart', method='filter_favorite'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(
                favorite__user=self.request.user, **{name: True}
            ).all()

        return queryset.exclude(
            favorite__user=self.request.user, **{name: True}
        ).all()


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name']
