from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django_extensions.validators import HexValidator

User = get_user_model()

NAME_MAX_LENGHT = 200
SLUG_MAX_LENGHT = 200
COLOR_MAX_LENGHT = 7
NUMBER_OF_VISIBLE_CHATACTERS = 15


class Tag(models.Model):
    """Модель таблицы Теги."""

    name = models.CharField(
        'Заголовок',
        max_length=NAME_MAX_LENGHT,
    )
    color = models.CharField(
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


class Ingredient(models.Model):
    """Модель таблицы Ингрединты."""

    name = models.CharField(
        'Заголовок',
        max_length=NAME_MAX_LENGHT,
    )
    measurement_unit = models.TextField(
        'Единицы измерения',
        default=None,
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class Recipe(models.Model):
    """Модель таблицы Рецепты."""

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
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
        verbose_name='Автор рецепта',
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
        verbose_name='Ингредиенты в рецепте',
        related_name='recipes',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipes',
    )
    amount = models.PositiveSmallIntegerField(
        'Мера',
    )

    class Meta:
        verbose_name = 'Колличество ингредиента в рецепте'
        verbose_name_plural = 'Колличество ингредиентов в рецепте'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='автор',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'following'], name='unique_follow'
            ),
        ]
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'


class UserRecipeAbstractModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe',
            ),
        ]
        abstract = True


class Favorite(UserRecipeAbstractModel):
    user = models.ForeignKey(
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        related_name='favorites',
        verbose_name='Избранный рецепт',
    )

    class Meta:

        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(UserRecipeAbstractModel):
    user = models.ForeignKey(
        related_name='purchases',
    )
    recipe = models.ForeignKey(
        related_name='purchases',
        verbose_name='Рецепт в списке покупок',
    )

    class Meta:

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
