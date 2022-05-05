from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.paginations import PagePagination
from api.permissions import IsAuthor
from api.serializers import (FavoriteSerializer, FollowSerializer,
                             FoodUserSerializer, IngredientSerializer,
                             RecipeSerializer, TagSerializer)
from api.utils import pdf
from recipe.models import Favorite, Ingredient, IngredientInRecipe, Recipe, Tag
from users.models import Follow, User


class FoodUserViewSet(UserViewSet):
    serializer_class = FoodUserSerializer
    queryset = User.objects.all()
    pagination_class = PagePagination

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        author_ids = Follow.objects.filter(
            user_id=self.request.user.id
        ).values_list('author', flat=True)
        data = self.filter_queryset(
            User.objects.filter(id__in=author_ids).all()
        )
        page = self.paginate_queryset(data)
        serializer = FollowSerializer(
            page, context={'request': request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        permission_classes=[IsAuthenticated],
        methods=['POST', 'DELETE'],
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if self.request.user.id == author:
                return Response(
                    {'errors': 'Вы не можете подписываться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Follow.objects.filter(
                author_id=author.id, user_id=self.request.user.id
            ).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Follow.objects.create(
                author_id=author.id, user_id=self.request.user.id
            )
            serializer = FollowSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if self.request.user.id == author:
                return Response(
                    {'errors': 'Вы не можете отписываться от самого себя'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            follow = Follow.objects.filter(
                author_id=author.id, user_id=self.request.user.id
            )
            if follow.exists():
                follow.delete()
                return Response(
                    {'status': 'Вы успешно отписались от пользователя'},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {'errors': 'Вы не подписаны на данного пользователя'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor]
    pagination_class = PagePagination
    filterset_class = RecipeFilter

    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='(?P<id>[0-9]+)/favorite',
    )
    def favorite(self, request, id):
        new_recipe = get_object_or_404(Recipe, id=id)

        if request.method == 'POST':
            recipe = Favorite.objects.get_or_create(
                recipe_id=id, user_id=self.request.user.id
            )[0]
            if recipe.favorite:
                raise ValidationError(
                    detail={
                        'error': [
                            'Рецепт уже добавлен в ваш список избранного'
                        ]
                    }
                )
            else:
                recipe.favorite = True
                recipe.save()
            serializer = FavoriteSerializer(new_recipe)
            return Response(serializer.data)
        if request.method == 'DELETE':
            recipe = Favorite.objects.get(
                recipe_id=id, user_id=self.request.user.id
            )
            if recipe.favorite is False:
                raise ValidationError(
                    detail={'error': ['Рецепта нет в вашем списке избранного']}
                )
            else:
                recipe.favorite = False
                recipe.save()
                return Response(
                    {'status': 'Рецепт удален из избранного'},
                    status=status.HTTP_200_OK,
                )

    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='(?P<id>[0-9]+)/shopping_cart',
    )
    def shopping_cart(self, request, id):
        new_recipe = get_object_or_404(Recipe, id=id)

        if request.method == 'POST':
            recipe = Favorite.objects.get_or_create(
                recipe_id=id, user_id=self.request.user.id
            )[0]
            if recipe.shopping_cart is True:
                raise ValidationError(
                    detail={
                        'error': ['Вы уже добавили рецепт в список покупок.']
                    }
                )
            else:
                recipe.shopping_cart = True
                recipe.save()
            serializer = FavoriteSerializer(new_recipe)
            return Response(serializer.data)
        if request.method == 'DELETE':
            recipe = Favorite.objects.get(
                recipe_id=id, user_id=self.request.user.id
            )
            if recipe.shopping_cart is False:
                raise ValidationError(
                    detail={'error': ['Рецепт не добавлен в список покупок']}
                )
            else:
                recipe.shopping_cart = False
                recipe.save()
                return Response(
                    {'status': 'Рецепт удален из списка покупок'},
                    status=status.HTTP_200_OK,
                )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
    )
    def get_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__favorite__user=request.user,
            recipe__favorite__shopping_cart=True
        ).values_list('amount',
                      'ingredient__pk',
                      'ingredient__name',
                      'ingredient__measurement_unit'
                      )
        data = dict()
        if not ingredients:
            raise ValidationError(
                detail={'error': ['Ваш список покупок пуст :(']}
            )
        for ingredient in ingredients:
            pk_number = ingredient[1]
            if pk_number in data:
                data[pk_number][
                    'amount'
                ] += ingredient[0]
            else:
                data.update(
                    {
                        pk_number: {
                            'name': ingredient[2],
                            'measurement_unit':
                                ingredient[3],
                            'amount': ingredient[0],
                        }
                    }
                )
        data = dict(sorted(data.items(), key=lambda item: item[1]['name']))
        return pdf(data)

    @staticmethod
    def post_method_for_actions(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        instance.delete()
