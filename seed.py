# seed.py
import os
from app import create_app, db
from app.models import Product, User

app = create_app()
app.app_context().push()

# Optionnel : vider les tables (uniquement en développement !)
# db.drop_all()
# db.create_all()

# ======================
# 📦 PRODUITS ARTISANAUX
# ======================

products_data = [
    # 👞 HOMME
    {
        "name": "Richelieu Classique en Cuir de Vache",
        "description": "Modèle intemporel fabriqué à Abidjan. Cuir pleine fleur, doublure en coton, semelle cousue main. Idéal pour le bureau ou les grandes occasions.",
        "price": 15000.00,
        "category": "Homme",
        "material": "Cuir de vache",
        "image_url": "image/brown-leather-shoes.jpg",
        "in_stock": True
    },
    {
        "name": "Bottes Cuir Épais - Collection Hiver",
        "description": "Chaudes et robustes, doublure en laine naturelle, semelle antidérapante. Parfaites pour la saison froide en Afrique de l’Ouest.",
        "price": 15000.00,
        "category": "Homme",
        "material": "Cuir épais",
        "image_url": "image/leather-boots.jpg",
        "in_stock": True
    },
    {
        "name": "Derbies Cuir Souple - Confort Quotidien",
        "description": "Légers, flexibles, conçus pour marcher toute la journée. Semelle en caoutchouc, montage artisanal à la main.",
        "price": 15000.00,
        "category": "Homme",
        "material": "Cuir souple",
        "image_url": "images/homme_soulier.jpg",
        "in_stock": True
    },
    {
        "name": "Mocassins Tressés - Édition Limitée",
        "description": "Inspirés des motifs traditionnels ivoiriens. Tressage main avec cuir et raphia local. Pièce unique, 100% made in Côte d’Ivoire.",
        "price": 15000.00,
        "category": "Homme",
        "material": "Cuir + Raphia",
        "image_url": "images/sandale_cuire_H1.jpg",
        "in_stock": True
    },

    # 👠 FEMME
    {
        "name": "Escarpins Talon Aiguille - Cuir Nappa",
        "description": "Élégance absolue. Talon 8 cm, bout pointu, semelle amortie. Doublure en cuir souple pour un confort maximal.",
        "price": 15000.00,
        "category": "Femme",
        "material": "Cuir Nappa",
        "image_url": "images/sandale_BM__Femme.jpg",
        "in_stock": True
    },
    {
        "name": "Sandales Été Tressées - Bleu Indigo",
        "description": "Légères, respirantes, teintes à l’indigo naturel. Tressage main par des artisanes de Grand-Bassam.",
        "price": 15000.00,
        "category": "Femme",
        "material": "Cuir tressé",
        "image_url": "images/Femme_semelle_Noire.jpg",
        "in_stock": True
    },
    {
        "name": "Bottines Cuir Velours - Automne",
        "description": "Chics et chaleureuses. Talon bloc 5 cm, fermeture éclair discrète. Parfaites pour la saison des pluies.",
        "price": 15000.00,
        "category": "Femme",
        "material": "Velours de cuir",
        "image_url": "images/Femme_semelle_maron.jpg",
        "in_stock": True
    },
    {
        "name": "Ballérimos Cuir Souple - Confort Absolu",
        "description": "Pour celles qui marchent beaucoup. Aucun talon, semelle ultra-souple, montage sans couture intérieure.",
        "price": 15000.00,
        "category": "Femme",
        "material": "Cuir souple",
        "image_url": "images/blanc_maron_femme.jpg",
        "in_stock": True
    },

    # 🔄 MIXTE
    {
        "name": "Espadrilles Coton Bio - Unisexe",
        "description": "Chaussures légères en coton biologique et semelle en corde naturelle. Idéales pour la plage ou la ville. Tailles homme et femme.",
        "price": 15000.00,
        "category": "Mixte",
        "material": "Coton bio + Corde",
        "image_url": "images/sandale_cuire_mixte.jpg",
        "in_stock": True
    },
    {
        "name": "Baskets Cuir Minimaliste - Édition Éco",
        "description": "Design épuré, 100% cuir recyclé, semelle en caoutchouc naturel. Fabriquées sans produits chimiques. Pour tous les jours.",
        "price": 15000.00,
        "category": "Mixte",
        "material": "Cuir recyclé",
        "image_url": "images/sandale_cuire_marron_Hom.jpg",
        "in_stock": True
    },
    {
        "name": "Chaussons Maison en Daim - Confort Intérieur",
        "description": "Doux, chauds, anti-dérapants. Doublure en laine de mouton. Parfaits pour la maison ou l’hôtel.",
        "price": 15000.00,
        "category": "Mixte",
        "material": "Daim",
        "image_url": "images/mixte123.jpg",
        "in_stock": True
    },
    {
        "name": "Tongs Artisanales en Caoutchouc - Collection Plage",
        "description": "Résistantes, flexibles, gravées à la main avec motifs adinkra. Idéales pour la mer, la piscine ou le marché.",
        "price": 15000.00,
        "category": "Mixte",
        "material": "Caoutchouc naturel",
        "image_url": "images/Homme_sandale.jpg",
        "in_stock": True
    }
]


# ======================
# 🚀 INSERTION DANS LA BASE
# ======================

def seed_products():
    for data in products_data:
        # Évite les doublons
        existing = Product.query.filter_by(name=data["name"]).first()
        if not existing:
            product = Product(**data)
            db.session.add(product)
    db.session.commit()
    print(f"✅ {len(products_data)} produits ajoutés à la base.")

# Exécution
if __name__ == '__main__':
    seed_products()
    print("\n🌱 Données initiales chargées avec succès !")