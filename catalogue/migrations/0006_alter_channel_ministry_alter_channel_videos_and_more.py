# Generated by Django 5.1 on 2024-08-25 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0005_alter_bible_book_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="channel",
            name="ministry",
            field=models.ManyToManyField(
                blank=True,
                help_text="The ministries related to the channel.",
                related_name="+",
                to="catalogue.ministry",
            ),
        ),
        migrations.AlterField(
            model_name="channel",
            name="videos",
            field=models.ManyToManyField(
                blank=True,
                help_text="The videos related to the channel.",
                related_name="+",
                to="catalogue.video",
            ),
        ),
        migrations.AlterField(
            model_name="demographic",
            name="series",
            field=models.ManyToManyField(
                blank=True,
                help_text="The series related to the channel.",
                related_name="+",
                to="catalogue.series",
            ),
        ),
        migrations.AlterField(
            model_name="demographic",
            name="topics",
            field=models.ManyToManyField(
                blank=True,
                help_text="The topics related to the channel.",
                related_name="+",
                to="catalogue.topic",
            ),
        ),
        migrations.AlterField(
            model_name="demographic",
            name="videos",
            field=models.ManyToManyField(
                blank=True,
                help_text="The vieos related to the channel.",
                related_name="+",
                to="catalogue.video",
            ),
        ),
        migrations.AlterField(
            model_name="ministry",
            name="channel",
            field=models.ManyToManyField(
                blank=True,
                help_text="The channels associated with minsitry.",
                related_name="+",
                to="catalogue.channel",
            ),
        ),
        migrations.AlterField(
            model_name="ministry",
            name="series",
            field=models.ManyToManyField(
                blank=True,
                help_text="The series associated with minsitry.",
                related_name="+",
                to="catalogue.series",
            ),
        ),
        migrations.AlterField(
            model_name="ministry",
            name="videos",
            field=models.ManyToManyField(
                blank=True,
                help_text="The videos associated with ministry.",
                related_name="+",
                to="catalogue.video",
            ),
        ),
        migrations.AlterField(
            model_name="series",
            name="bible_book",
            field=models.ManyToManyField(
                blank=True,
                help_text="The Bible books related to the series.",
                to="catalogue.bible_book",
            ),
        ),
        migrations.AlterField(
            model_name="series",
            name="ministry",
            field=models.ManyToManyField(
                blank=True,
                help_text="The ministry related to the series.",
                related_name="+",
                to="catalogue.ministry",
            ),
        ),
        migrations.AlterField(
            model_name="series",
            name="speaker",
            field=models.ManyToManyField(
                blank=True,
                help_text="The speaker related to the series.",
                related_name="+",
                to="catalogue.speaker",
            ),
        ),
        migrations.AlterField(
            model_name="series",
            name="topic",
            field=models.ManyToManyField(
                blank=True,
                help_text="The topic related to the series.",
                related_name="+",
                to="catalogue.topic",
            ),
        ),
        migrations.AlterField(
            model_name="series",
            name="videos",
            field=models.ManyToManyField(
                blank=True,
                help_text="The videos related to the series.",
                related_name="+",
                to="catalogue.video",
            ),
        ),
        migrations.AlterField(
            model_name="speaker",
            name="series",
            field=models.ManyToManyField(
                blank=True,
                help_text="The videos related to series.",
                related_name="+",
                to="catalogue.series",
            ),
        ),
        migrations.AlterField(
            model_name="speaker",
            name="videos",
            field=models.ManyToManyField(
                blank=True,
                help_text="The videos related to video.",
                related_name="+",
                to="catalogue.video",
            ),
        ),
        migrations.AlterField(
            model_name="topic",
            name="series",
            field=models.ManyToManyField(
                blank=True,
                help_text="Select series for this topic",
                related_name="+",
                to="catalogue.series",
            ),
        ),
        migrations.AlterField(
            model_name="topic",
            name="videos",
            field=models.ManyToManyField(
                blank=True,
                help_text="Select videos for this topic",
                related_name="+",
                to="catalogue.video",
            ),
        ),
        migrations.AlterField(
            model_name="video",
            name="bible_book",
            field=models.ManyToManyField(
                blank=True,
                help_text="The bible books covered in the video.",
                to="catalogue.bible_book",
            ),
        ),
        migrations.AlterField(
            model_name="video",
            name="demographic",
            field=models.ManyToManyField(
                blank=True,
                help_text="The video's demographic.",
                to="catalogue.demographic",
            ),
        ),
        migrations.AlterField(
            model_name="video",
            name="ministry",
            field=models.ManyToManyField(
                blank=True,
                help_text="The ministries associated with the video.",
                to="catalogue.ministry",
            ),
        ),
        migrations.AlterField(
            model_name="video",
            name="speaker",
            field=models.ManyToManyField(
                blank=True,
                help_text="The speakers/artist in the video.",
                to="catalogue.speaker",
            ),
        ),
    ]
