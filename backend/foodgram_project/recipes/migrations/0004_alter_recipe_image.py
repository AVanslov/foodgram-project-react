# Generated by Django 4.2 on 2024-05-01 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=None, upload_to='image', verbose_name='Фото рецепта'),
        ),
    ]
