from django.contrib.auth.models import User
from django.db import models

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
        related_name='recipes',
    )
    tag = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes',
    )
    ingredient = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
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

    class Meta:
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = 'Количество ингрединтов в рецептах' 


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
