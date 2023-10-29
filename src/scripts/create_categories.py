from agenda_culturel.models import Category

def run():
    # concert, théâtre, jeune public, danse, arts du spectacle, exposition
    # conférence, nature, 
    # divers

    categories = [
        ("Théâtre", "Au théâtre", "THÉ"),
        ("Concert", "Concerts", "CCR"),
        ("Danse", "En danse", "DSE"),
        ("Arts du spectacle", None, "SPE"),
        ("Jeune public", "Pour le jeune public", "JEP"),
        ("Exposition", "Expositions", "EXP"),
        ("Conférence", "Conférences", "CNF"),
        ("Nature", "Événements nature", "NTR"),
        ("Autre", "Autres événements", "ATR")
    ]

    if len(Category.objects.all()) == 0:
        print("On créée des catégories")
        for c in categories:
            cat = Category(name=c[0], alt_name = c[1] if c[1] is not None else c[0], codename=c[2])
            cat.save()

