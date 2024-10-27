# Generated by Django 5.0.4 on 2024-07-28 13:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Bible_Book",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "order",
                    models.CharField(
                        help_text="Integer used to sort books into order.", max_length=3
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        choices=[
                            ("GEN", "Genesis"),
                            ("EXO", "Exodus"),
                            ("LEV", "Leviticus"),
                            ("NUM", "Numbers"),
                            ("DEU", "Deuteronomy"),
                            ("JOS", "Joshua"),
                            ("JUD", "Judges"),
                            ("RUT", "Ruth"),
                            ("1SA", "1 Samuel"),
                            ("2SA", "2 Samuel"),
                            ("1KI", "1 Kings"),
                            ("2KI", "2 Kings"),
                            ("1CH", "1 Chronicles"),
                            ("2CH", "2 Chronicles"),
                            ("EZR", "Ezra"),
                            ("NEH", "Nehemiah"),
                            ("EST", "Esther"),
                            ("JOB", "Job"),
                            ("PSA", "Psalms"),
                            ("PRO", "Proverbs"),
                            ("ECC", "Ecclesiastes"),
                            ("SOG", "Song of Solomon"),
                            ("ISA", "Isaiah"),
                            ("JER", "Jeremiah"),
                            ("LAM", "Lamentations"),
                            ("EZE", "Ezekiel"),
                            ("DAN", "Daniel"),
                            ("HOS", "Hosea"),
                            ("JOEL", "Joel"),
                            ("AMO", "Amos"),
                            ("OBA", "Obadiah"),
                            ("JON", "Jonah"),
                            ("MIC", "Micah"),
                            ("NAH", "Nahum"),
                            ("HAB", "Habakkuk"),
                            ("ZEP", "Zephaniah"),
                            ("HAG", "Haggai"),
                            ("ZECH", "Zechariah"),
                            ("MAL", "Malachi"),
                            ("MAT", "Matthew"),
                            ("MAR", "Mark"),
                            ("LUKE", "Luke"),
                            ("JOHN", "John"),
                            ("ACT", "Acts"),
                            ("ROM", "Romans"),
                            ("1CO", "1 Corinthians"),
                            ("2CO", "2 Corinthians"),
                            ("GAL", "Galatians"),
                            ("EPH", "Ephesians"),
                            ("PHI", "Philippians"),
                            ("COL", "Colossians"),
                            ("1TH", "1 Thessalonians"),
                            ("2TH", "2 Thessalonians"),
                            ("1TI", "1 Timothy"),
                            ("2TI", "2 Timothy"),
                            ("TIT", "Titus"),
                            ("PHM", "Philemon"),
                            ("HEB", "Hebrews"),
                            ("JAS", "James"),
                            ("1PE", "1 Peter"),
                            ("2PE", "2 Peter"),
                            ("1JO", "1 John"),
                            ("2JO", "2 John"),
                            ("3JO", "3 John"),
                            ("JUD", "Jude"),
                            ("REV", "Revelation"),
                        ],
                        help_text="Three or four letter code related to each bible book.",
                        max_length=4,
                        unique=True,
                    ),
                ),
                (
                    "summary",
                    models.TextField(
                        blank=True,
                        help_text="Summary of book of the bible.",
                        max_length=5000,
                        null=True,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("LAW", "Law"),
                            ("HIS", "History"),
                            ("POE", "Poetry"),
                            ("PRO", "Prophecy"),
                            ("GOS", "Gospel"),
                            ("EPI", "Epistle"),
                            ("APO", "Apocalyptic"),
                        ],
                        help_text="Three letter code related to the type of book, e.g. Law, History, Poetry, Prophecy, Gospel, Epistle, Apocalyptica.",
                        max_length=3,
                        unique=True,
                    ),
                ),
            ],
            options={
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="Channel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(help_text="The channel name.", max_length=200),
                ),
                (
                    "summary",
                    models.TextField(
                        blank=True,
                        help_text="The summary of the channel",
                        max_length=5000,
                        null=True,
                    ),
                ),
                (
                    "type",
                    models.CharField(help_text="The channel type.", max_length=200),
                ),
                (
                    "channel_url",
                    models.URLField(help_text="The channel url.", unique=True),
                ),
                (
                    "trusted",
                    models.BooleanField(help_text="Whether the channel is trusted."),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Label",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "label_series",
                    models.CharField(
                        help_text="Admin Label Related to the video's series.",
                        max_length=1000,
                    ),
                ),
                (
                    "label_subseries",
                    models.CharField(
                        help_text="Admin Label Related to the video's subseries.",
                        max_length=1000,
                    ),
                ),
                (
                    "label_episode",
                    models.CharField(
                        help_text="Admin Label Related to the video's episode.",
                        max_length=1000,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Ministry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(help_text="The ministry's name.", max_length=200),
                ),
                (
                    "summary",
                    models.TextField(
                        blank=True,
                        help_text="A brief summary of the ministry.",
                        max_length=5000,
                        null=True,
                    ),
                ),
                (
                    "thumbnail",
                    models.CharField(
                        help_text="The thumbnail for the ministry area.", max_length=200
                    ),
                ),
                (
                    "channel",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The channels associated with minsitry.",
                        null=True,
                        related_name="+",
                        to="catalogue.channel",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="channel",
            name="ministry",
            field=models.ManyToManyField(
                blank=True,
                help_text="The ministries related to the channel.",
                null=True,
                related_name="+",
                to="catalogue.ministry",
            ),
        ),
        migrations.CreateModel(
            name="Series",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="The name of the series.", max_length=200
                    ),
                ),
                (
                    "summary",
                    models.TextField(
                        blank=True,
                        help_text="The summary/description of the series.",
                        max_length=5000,
                        null=True,
                    ),
                ),
                ("year_start", models.CharField(help_text="The ", max_length=100)),
                ("year_end", models.CharField(max_length=100)),
                (
                    "bible_book",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The Bible books related to the series.",
                        null=True,
                        to="catalogue.bible_book",
                    ),
                ),
                (
                    "ministry",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The ministry related to the series.",
                        null=True,
                        related_name="+",
                        to="catalogue.ministry",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="ministry",
            name="series",
            field=models.ManyToManyField(
                blank=True,
                help_text="The series associated with minsitry.",
                null=True,
                related_name="+",
                to="catalogue.series",
            ),
        ),
        migrations.AddField(
            model_name="channel",
            name="series",
            field=models.ForeignKey(
                blank=True,
                help_text="The series related to the channel.",
                null=True,
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="+",
                to="catalogue.series",
            ),
        ),
        migrations.CreateModel(
            name="Speaker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("bio", models.TextField(max_length=5000)),
                ("thumbnail", models.CharField(max_length=200)),
                (
                    "series",
                    models.ManyToManyField(
                        blank=True, null=True, related_name="+", to="catalogue.series"
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="series",
            name="speaker",
            field=models.ManyToManyField(
                blank=True,
                help_text="The speaker related to the series.",
                null=True,
                related_name="+",
                to="catalogue.speaker",
            ),
        ),
        migrations.CreateModel(
            name="Topic",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Enter a topic or theme", max_length=200, unique=True
                    ),
                ),
                (
                    "summary",
                    models.TextField(
                        blank=True,
                        help_text="Enter a brief summary of the topic",
                        max_length=5000,
                        null=True,
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        help_text="Enter the category of the topic",
                        max_length=200,
                        unique=True,
                    ),
                ),
                (
                    "series",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Select series for this topic",
                        null=True,
                        related_name="+",
                        to="catalogue.series",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="series",
            name="topic",
            field=models.ManyToManyField(
                blank=True,
                help_text="The topic related to the series.",
                null=True,
                related_name="+",
                to="catalogue.topic",
            ),
        ),
        migrations.CreateModel(
            name="Demographic",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="The name of the demographic e.g. Kids, searchers.",
                        max_length=200,
                    ),
                ),
                (
                    "summary",
                    models.TextField(
                        help_text="A summary/description of the demographic.",
                        max_length=5000,
                    ),
                ),
                (
                    "thumbnail",
                    models.CharField(
                        help_text="The thumbnail for the demographic.", max_length=200
                    ),
                ),
                (
                    "series",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The series related to the channel.",
                        null=True,
                        related_name="+",
                        to="catalogue.series",
                    ),
                ),
                (
                    "topics",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The topics related to the channel.",
                        null=True,
                        related_name="+",
                        to="catalogue.topic",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Video",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "url",
                    models.URLField(
                        help_text="A link to where the video is hosted.", unique=True
                    ),
                ),
                (
                    "id_number",
                    models.CharField(
                        help_text="A unique video identifier generated e.g.YT1234",
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "number_in_series",
                    models.IntegerField(
                        blank=True,
                        help_text="If part of a series provide the number in the series.",
                        null=True,
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="The title of the video.", max_length=200
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="Enter a brief description of the video <5000 chars.",
                        max_length=5000,
                    ),
                ),
                (
                    "date_recorded",
                    models.DateField(
                        blank=True,
                        help_text="The date the video was recorded.",
                        null=True,
                    ),
                ),
                (
                    "date_created",
                    models.DateField(help_text="The date a video is uploaded."),
                ),
                (
                    "date_modified",
                    models.DateField(
                        blank=True,
                        help_text=" The last time the video data was edited.",
                        null=True,
                    ),
                ),
                (
                    "is_livestream",
                    models.BooleanField(
                        default=False, help_text="Whether the video was a live stream."
                    ),
                ),
                (
                    "bible_book",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The bible books covered in the video.",
                        null=True,
                        to="catalogue.bible_book",
                    ),
                ),
                (
                    "channel",
                    models.ForeignKey(
                        help_text="The channel for the video.",
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="catalogue.channel",
                    ),
                ),
                (
                    "demographic",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The video's demographic.",
                        null=True,
                        to="catalogue.demographic",
                    ),
                ),
                (
                    "labels",
                    models.ForeignKey(
                        blank=True,
                        help_text="Labels for internal admin use.",
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="catalogue.label",
                    ),
                ),
                (
                    "ministry",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The ministries associated with the video.",
                        null=True,
                        to="catalogue.ministry",
                    ),
                ),
                (
                    "series",
                    models.ForeignKey(
                        blank=True,
                        help_text="The series the video is part of.",
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="catalogue.series",
                    ),
                ),
                (
                    "speaker",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The speakers in the video.",
                        null=True,
                        to="catalogue.speaker",
                    ),
                ),
                (
                    "topic",
                    models.ManyToManyField(
                        help_text="Select topics for this video.", to="catalogue.topic"
                    ),
                ),
            ],
            options={
                "ordering": ["date_created"],
            },
        ),
        migrations.AddField(
            model_name="topic",
            name="videos",
            field=models.ManyToManyField(
                blank=True,
                help_text="Select videos for this topic",
                null=True,
                related_name="+",
                to="catalogue.video",
            ),
        ),
        migrations.AddField(
            model_name="speaker",
            name="videos",
            field=models.ManyToManyField(
                blank=True, null=True, related_name="+", to="catalogue.video"
            ),
        ),
        migrations.AddField(
            model_name="series",
            name="videos",
            field=models.ManyToManyField(
                blank=True,
                help_text="The videos related to the series.",
                null=True,
                related_name="+",
                to="catalogue.video",
            ),
        ),
        migrations.AddField(
            model_name="ministry",
            name="videos",
            field=models.ManyToManyField(
                blank=True,
                help_text="The videos associated with ministry.",
                null=True,
                related_name="+",
                to="catalogue.video",
            ),
        ),
        migrations.AddField(
            model_name="demographic",
            name="videos",
            field=models.ManyToManyField(
                blank=True,
                help_text="The vieos related to the channel.",
                null=True,
                related_name="+",
                to="catalogue.video",
            ),
        ),
        migrations.AddField(
            model_name="channel",
            name="videos",
            field=models.ManyToManyField(
                blank=True,
                help_text="The videos related to the channel.",
                null=True,
                related_name="+",
                to="catalogue.video",
            ),
        ),
    ]
