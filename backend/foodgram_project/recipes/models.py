from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MinValueValidator,
)
from django.db import models
from django.db.models import UniqueConstraint

from .color_generator import color_generator
from .constants import (
    AMOUNT_MIN_VALUE,
    COLOR_MAX_LENGHT,
    COOKING_TIME_MIN_VALUE,
    EMAIL_MAX_LENGHT,
    FIRSTNAME_MAX_LENGHT,
    LASTNAME_MAX_LENGHT,
    NAME_MAX_LENGHT,
    SLUG_MAX_LENGHT,
    USERNAME_MAX_LENGHT,
)
from .validators import (
    isValidHexaCode,
    validate_found_special_symbols,
    validate_not_djoser_endpoints,
)


class User(AbstractUser):

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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

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
        unique=True,
        max_length=COLOR_MAX_LENGHT,
        default=color_generator,
        validators=[isValidHexaCode],
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

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель таблицы Рецепты."""

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Продукты',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    image = models.ImageField(
        'Фото рецепта',
        upload_to='images/',
        default=None,
    )
    name = models.CharField(
        'Заголовок',
        max_length=NAME_MAX_LENGHT,
    )
    text = models.TextField(
        'Описание рецепта',
        default='Описание рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
        help_text='Введите время приготовления в минутах',
        validators=[MinValueValidator(limit_value=COOKING_TIME_MIN_VALUE)],
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

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Промежуточная таблица Рецептов и ингредиентов
    с добавочным столбцом Количество.
    """

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Продукт в рецепте',
        related_name='recipe_ingredients',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients',
    )
    amount = models.IntegerField(
        'Мера',
        validators=[MinValueValidator(limit_value=AMOUNT_MIN_VALUE)],
    )

    class Meta:
        verbose_name = 'Мера продукта в рецепте'
        verbose_name_plural = 'Меры продуктов в рецепте'
        ordering = ('ingredient__name',)

    def __str__(self):
        return f'{self.ingredient} {self.recipe} {self.amount}'


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
        ordering = ('user__username',)


class UserRecipeModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_%(class)s',
            ),
        ]
        default_related_name = '%(class)s'
        ordering = ('user__username',)

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Favorite(UserRecipeModel):

    class Meta(UserRecipeModel.Meta):
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(UserRecipeModel):

    class Meta(UserRecipeModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
