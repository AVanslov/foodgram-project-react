from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()

TITLE_MAX_LENGHT = 128
NUMBER_OF_VISIBLE_CHATACTERS = 15


class TitleModel(models.Model):
    """Модель абстрактного класса Заголовок."""

    name = models.CharField(
        'Заголовок',
        max_length=TITLE_MAX_LENGHT,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Tag(TitleModel):
    """Модель таблицы Теги."""

    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        max_length=64,
        help_text=(
            'Идентификатор страницы для URL; разрешены символы латиницы, '
            'цифры, дефис и подчёркивание.'
        ),
    )
    color = models.CharField(
        max_length=16,
        default='#ff0000',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(TitleModel):
    """Модель таблицы Ингрединты."""

    measurement_unit = models.TextField(
        'Единицы измерения',
        default=None,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(TitleModel):
    """Модель таблицы Рецепты."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='Author',
    )
    image = models.ImageField(
        'Фото рецепта',
        upload_to='image/',
        null=False,
        default=None,
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ingredients',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )
    text = models.TextField(
        'Описание рецепта',
        default='',
        max_length=3600,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        help_text='Введите время приготовления в минутах',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']


class RecipeIngredient(models.Model):
    """
    Промежуточная таблица Рецептов и ингредиентов
    с добавочным столбцом Количество.
    """

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты в рецепте',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    quantity = models.PositiveSmallIntegerField(
        'Колличество ингредиента',
    )

    class Meta:
        verbose_name = 'Колличество ингредиента в рецепте'
        verbose_name_plural = 'Колличество ингредиентов в рецепте'


class RecipeTag(models.Model):
    """
    Промежуточная таблица Рецептов и тегов.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Рецепт и его Теги'
        verbose_name_plural = 'Рецепт и его Теги'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Follower",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Following",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "following"], name="unique_follow"
            ),
        ]
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='User',
    )
    favorite_recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Favorite Recipe',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'favorite_recipe'],
                name='unique_favorite_recipe',
            ),
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='in_cart',
        verbose_name='User',
    )
    recipe_in_cart = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='put_in_cart_by',
        verbose_name='Recipe in Shopping Cart',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe_in_cart'],
                name='unique_recipe_in_cart',
            ),
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
