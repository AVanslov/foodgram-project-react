from django.contrib.auth.models import AbstractBaseUser
from django.core.validators import (
    MinValueValidator,
)
from django.db import models
from django.db.models import UniqueConstraint
from django_extensions.validators import HexValidator

from .validators import (
    validate_found_special_symbols,
    validate_not_djoser_endpoints
)

FIRSTNAME_MAX_LENGHT = 150
LASTNAME_MAX_LENGHT = 150
USERNAME_MAX_LENGHT = 150
EMAIL_MAX_LENGHT = 254

NAME_MAX_LENGHT = 200
SLUG_MAX_LENGHT = 200
COLOR_MAX_LENGHT = 7
NUMBER_OF_VISIBLE_CHATACTERS = 15


class User(AbstractBaseUser):

    first_name = models.CharField(
        verbose_name='Имя', max_length=FIRSTNAME_MAX_LENGHT,
    )
    last_name = models.CharField(
        verbose_name='Фамилия', max_length=LASTNAME_MAX_LENGHT,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=USERNAME_MAX_LENGHT,
        unique=True,
        validators=[
            validate_found_special_symbols,
            validate_not_djoser_endpoints
        ]
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=EMAIL_MAX_LENGHT,
        unique=True,
    )

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class Tag(models.Model):
    """Модель таблицы Теги."""

    name = models.CharField(
        'Заголовок',
        max_length=NAME_MAX_LENGHT,
    )
    color = models.CharField(
        'Цвет',
        max_length=COLOR_MAX_LENGHT,
        default='#ff0000',
        validators=[HexValidator(length=COLOR_MAX_LENGHT)],
    )
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        max_length=SLUG_MAX_LENGHT,
        help_text=(
            'Идентификатор страницы для URL; разрешены символы латиницы, '
            'цифры, дефис и подчёркивание.'
        ),
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)


class Ingredient(models.Model):
    """Модель таблицы Ингрединты."""

    name = models.CharField(
        'Заголовок',
        max_length=NAME_MAX_LENGHT,
    )
    measurement_unit = models.TextField(
        'Мера',
        default=None,
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)


class Recipe(models.Model):
    """Модель таблицы Рецепты."""

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Продукт',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    image = models.ImageField(
        'Фото рецепта',
        upload_to='image/',
        null=False,
        default=None,
    )
    name = models.CharField(
        'Заголовок',
        max_length=NAME_MAX_LENGHT,
    )
    text = models.TextField(
        'Описание рецепта',
        default='',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
        help_text='Введите время приготовления в минутах',
        validators=[MinValueValidator(limit_value=1)],
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)


class RecipeIngredient(models.Model):
    """
    Промежуточная таблица Рецептов и ингредиентов
    с добавочным столбцом Количество.
    """

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Продукты в рецепте',
        related_name='ingredients_in_current_recipe',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipes_with_current_ingredient',
    )
    amount = models.PositiveSmallIntegerField(
        'Мера',
    )

    class Meta:
        verbose_name = 'Колличество продукта в рецепте'
        verbose_name_plural = 'Колличество продуктов в рецепте'


class Follow(models.Model):
    """
    Модель для связи между автором и подписчиком.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'following'], name='unique_follow'
            ),
        ]
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'


class UserRecipeModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.user} {self.recipe}'

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe',
            ),
        ]


class Favorite(UserRecipeModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранный рецепт',
    )

    class Meta:

        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(UserRecipeModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchases',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name='Рецепт в списке покупок',
    )

    class Meta:

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
