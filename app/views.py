import django
from inertia import render


def index(request):
    django_version = django.get_version()

    video_info = {
        101: ('Galatians 1:1-23 - No Other Gospel - Jesmond Parish - Sermon', "7 Jan '24 Jonathan Pryke - The gospel rescues us from the curse. If we teach a distorted gospel that destroys the blessing of the gospel"),
        102: ('Galatians 2:1-14 - Paul: An Apostle - Jesmond Parish - Sermon', "14 Jan '24 Jonathan Pryke - What's your spiritual history? Jonathan explores Paul's apostolic authority through the lens of his persecution of the church"),
        103: ('Galatians 2:15-21 - Is Jesus Enough? - Jesmond Parish - Sermon', "21 Jan '24 Ian Garrett - Galatians is a 'spiritual vaccine' to protect you from those who tell you that Jesus isn't enough. Ian Garrett explores a situation where this was happening in the early church"),
        104: ('Galatians 3:1-14 - Getting Right with God - Jesmond Parish - Sermon - Clayton TV', "28 Jan '24 Ian Garrett - Your relationship with God depends 100% on the cross! Ian Garrett explores how a relationship with God's has always and will always begin and continue with grace from God."),
        105: ('Galatians 4:1-31 - From Slavery to Freedom - Jesmond Parish - Sermon', "18 Feb '24 Jonathan Pryke - How easily do you lose sight of God's love for us and amazing grace towards us? Jonathan Pryke walks us through our past slavery to sin before we came to Christ and our current freedom living for him."),
        106: ('Galatians 5:1-12 - Guarding Gospel Freedom - Jesmond Parish - Sermon', ''),
        107: ('Galatians 5:13-25 - How Knowing Jesus Changes You - Jesmond Parish - Sermon', "17 March '24 Ian Garrett - What does gospel freedom enables and produce? Ian Garrett explains what we are and are not freed for."),
        108: ('Galatians 6:1-18 - Living in the Light of the Cross - Jesmond Parish - Sermon ', "24 March '24 Ian Garrett - Don’t evaluate your Christian life by comparing yourself with your Christian neighbour"),
    }

    # Get value of a HTTP request parameter ?sort=xyz
    sort_mode = request.GET.get("sort")

    # Use a lambda to sort based on a specific field from the dictionary
    # The sorted() function passes the lambda a dictionary key,
    # it looks up that key and returns one of the fields attached to it
    if sort_mode == "title" :
        video_list_sorted = [video_info[i] for i in sorted(video_info, key=lambda i: video_info[i][0])]
    elif sort_mode == "summary" :
        video_list_sorted = [video_info[i] for i in sorted(video_info, key=lambda i: video_info[i][1])]
    else : # Unsorted
        video_list_sorted = [video_info[i] for i in video_info.keys()]

    return render(request, 'Welcome', {
        'djangoVersion': django_version,
        'videoInfo': video_list_sorted,
        'sortMode': sort_mode,
    })
