from agenda_culturel.models import Category

def run():
    # concert, théâtre, jeune public, danse, arts du spectacle, exposition
    # conférence, nature, 
    # divers

    categories = [
        ("Théâtre", "THÉ"),
        ("Concert", "CCR"),
        ("Danse", "DSE"),
        ("Arts du spectacle", "SPE"),
        ("Jeune public", "JEP"),
        ("Exposition", "EXP"),
        ("Conférence", "CNF"),
        ("Nature", "NTR"),
        ("Divers", "DIV")
    ]

    if len(Category.objects.all()) == 0:
        print("On créée des catégories")
        for c in categories:
            cat = Category(name=c[0], codename=c[1])
            cat.save()

