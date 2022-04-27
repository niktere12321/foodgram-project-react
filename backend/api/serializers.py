from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipe.models import Favorite, Ingredient, IngredientInRecipe, Recipe, Tag
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator
from users.models import Follow, User


class FoodUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        model = User
        extra_kwargs = {'password': {'write_only': True}}


class FoodUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            author_id=obj.id, user_id=user.id
        ).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Recipe


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = Ingredient
        read_only_fields = ['id', 'name', 'measurement_unit']

        def get_amount(self, obj):
            return obj.ingredientinrecipe.values('amount')[0].get('amount')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeSerializer(serializers.ModelSerializer):
    author = FoodUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipe

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredient_in_recipe__amount'),
        )
        return ingredients

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        recipe = Favorite.objects.filter(
            recipe_id=obj.id, user_id=user.id
        ).first()
        if recipe:
            return recipe.favorite
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        recipe = Favorite.objects.filter(
            recipe_id=obj.id, user_id=user.id
        ).first()
        if recipe:
            return recipe.shopping_cart
        return False

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'error': 'Необходим хотя бы 1 ингредиент'}
            )
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_item['id']
            )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальными'
                )
            ingredient_list.append(ingredient)

        data['ingredients'] = ingredients
        return data

    def create(self, validated_data):

        ingredients_data = validated_data.pop('ingredients')
        tag_ids = Tag.objects.all().values_list('id', flat=True)
        tag_id = self.context.get('request').data['tags']

        for id in tag_id:
            if id not in tag_ids:
                raise ValidationError(
                    detail={'tags': ['Такого тэга не существует :(']}
                )

        recipe = super(RecipeSerializer, self).create(validated_data)

        for ingredient in ingredients_data:
            try:
                get_ingredient = Ingredient.objects.get(id=ingredient['id'])
                IngredientInRecipe.objects.update_or_create(
                    recipe=recipe,
                    ingredient=get_ingredient,
                    amount=ingredient['amount'],
                )
            except Ingredient.DoesNotExist:
                raise ValidationError(
                    detail={
                        'ingredients': ['Такого ингредиента не существует :(']
                    }
                )

        return recipe


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            author_id=obj.id, user_id=user.id
        ).exists()

    def get_recipes(self, obj):
        try:
            count = int(self.context.GET['recipes_limit'])
            recipes = (
                Recipe.objects.filter(author_id=obj.id)
                .all()
                .prefetch_related(count)
            )
        except AttributeError:
            recipes = Recipe.objects.filter(author_id=obj.id).all()
        return FavoriteSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author_id=obj.id).count()
