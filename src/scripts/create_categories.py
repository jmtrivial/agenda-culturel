from agenda_culturel.models import Category

def run():
    # concert, théâtre, jeune public, danse, arts du spectacle, exposition
    # conférence, nature, 
    # divers

    categories = [
        ("Théâtre", "Au théâtre", "T"),
        ("Concert", "Concerts", "C"),
        ("Danse", "Danse", "D"),
        ("Arts du spectacle", None, "S"),
        ("Jeune public", "Pour le jeune public", "J"),
        ("Exposition", "Expositions", "E"),
        ("Conférence", "Conférences", "C"),
        ("Nature", "Événements nature", "N"),
        ("Autre", "Autres événements", "A")
    ]

    if len(Category.objects.all()) <= 1:
        print("On créée des catégories")
        for c in categories:
            cat = Category(name=c[0], alt_name = c[1] if c[1] is not None else c[0], codename=c[2])
            cat.save()

