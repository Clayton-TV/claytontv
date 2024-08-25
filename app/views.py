import django
from inertia import render


def index(request):
    # TODO: replace with db query
    videos = [
        {
            'id': 101,
            'title': 'Galatians 1:1-23 - No Other Gospel - Jesmond Parish - Sermon',
            'description': "7 Jan '24 Jonathan Pryke - The gospel rescues us from the curse. If we teach a distorted gospel that destroys the blessing of the gospel"
        },
        {
            'id': 102,
            'title': 'Galatians 2:1-14 - Paul: An Apostle - Jesmond Parish - Sermon',
            'description': "14 Jan '24 Jonathan Pryke - What's your spiritual history? Jonathan explores Paul's apostolic authority through the lens of his persecution of the church"
        },
        {
            'id': 103,
            'title': 'Galatians 2:15-21 - Is Jesus Enough? - Jesmond Parish - Sermon',
            'description': "21 Jan '24 Ian Garrett - Galatians is a 'spiritual vaccine' to protect you from those who tell you that Jesus isn't enough. Ian Garrett explores a situation where this was happening in the early church"
        },
        {
            'id': 104,
            'title': 'Galatians 3:1-14 - Getting Right with God - Jesmond Parish - Sermon - Clayton TV',
            'description': "28 Jan '24 Ian Garrett - Your relationship with God depends 100% on the cross! Ian Garrett explores how a relationship with God's has always and will always begin and continue with grace from God."
        },
        {
            'id': 105,
            'title': 'Galatians 4:1-31 - From Slavery to Freedom - Jesmond Parish - Sermon',
            'description': "18 Feb '24 Jonathan Pryke - How easily do you lose sight of God's love for us and amazing grace towards us? Jonathan Pryke walks us through our past slavery to sin before we came to Christ and our current freedom living for him."
        },
        {
            'id': 106,
            'title': 'Galatians 5:1-12 - Guarding Gospel Freedom - Jesmond Parish - Sermon',
            'description': ""
        },
        {
            'id': 107,
            'title': 'Galatians 5:13-25 - How Knowing Jesus Changes You - Jesmond Parish - Sermon',
            'description': "17 March '24 Ian Garrett - What does gospel freedom enables and produce? Ian Garrett explains what we are and are not freed for."
        },
        {
            'id': 108,
            'title': 'Galatians 6:1-18 - Living in the Light of the Cross - Jesmond Parish - Sermon ',
            'description': "24 March '24 Ian Garrett - Don’t evaluate your Christian life by comparing yourself with your Christian neighbour"
        },
    ]

    return render(request, 'Welcome', {
        'videos': videos,
    })
