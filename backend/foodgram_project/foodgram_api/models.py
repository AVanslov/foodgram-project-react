from django.contrib.auth.models import User
from django.db import models

TITLE_MAX_LENGHT = 128
NUMBER_OF_VISIBLE_CHATACTERS = 15


class TitleModel(models.Model):
    """Модель абстрактного класса Заголовок."""

    title = models.CharField(
        'Заголовок',
        max_length=TITLE_MAX_LENGHT,
    )

    class Meta:
        abstract = True


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


class IngredientType(TitleModel):
    """Модель таблицы Единицы измерения ингредиентов."""

    pass


class Ingredient(TitleModel):
    """Модель таблицы Ингрединты."""

    ingredient_type = models.OneToOneField(
        IngredientType,
        on_delete=models.CASCADE,
    )


class Recipe(TitleModel):
    """Модель таблицы Рецепты."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )


class RecipeIngredients(models.Model):
    """
    Промежуточная таблица Рецептов и ингредиентов
    с добавочным столбцом Количество.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    quantity = models.FloatField(
        'Количество',
    )
