from inertia import render


def index(request):
    return render(request, "CatalogueIndex", {
        "foo": "bar",
    })
