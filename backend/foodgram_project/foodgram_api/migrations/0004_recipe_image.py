# Generated by Django 3.2.16 on 2024-03-31 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram_api', '0003_tag_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, upload_to='recipe_images', verbose_name='Фото рецепта'),
        ),
    ]
