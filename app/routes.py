from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from werkzeug.security import check_password_hash
from flask_login import LoginManager, login_required
from .models import Product, User
import urllib.parse
from functools import wraps
from . import db

main = Blueprint('main', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Veuillez vous connecter pour accéder à cette page.", "warning")
            return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
def index():
    featured = Product.query.filter_by(in_stock=True).limit(6).all()
    return render_template('index.html', featured=featured)

@main.route('/mentions-legales')
def mentions_legales():
    return render_template('mentions-legales.html')

@main.route('/cgu')
def cgu():
    return render_template('cgu.html')

@main.route('/politique-de-confidentialite')
def politique_confidentialite():
    return render_template('politique-de-confidentialite.html')

@main.route('/politique-de-retour')
def politique_retour():
    return render_template('politique-de-retour.html')

@main.route('/a-propos')
def a_propos():
    return render_template('a-propos.html')

@main.route('/clear-cart')
@login_required
def clear_cart():
    # Vider uniquement le panier, pas la session utilisateur
    if 'cart' in session:
        session['cart'] = {'items': {}, 'shipping_country': 'CIV'}
    flash("Votre panier a été vidé.", "info")
    return redirect(url_for('main.cart'))

@main.route('/update-shipping', methods=['POST'])
@login_required
def update_shipping():
    country = request.form.get('country')
    if country not in ['CIV', 'International']:
        country = 'CIV'
    
    if 'cart' not in session:
        session['cart'] = {'items': {}, 'shipping_country': 'CIV'}
    session['cart']['shipping_country'] = country
    return redirect(url_for('main.cart'))

@main.route('/shop')
def shop():
    category = request.args.get('category')
    if category:
        products = Product.query.filter_by(category=category, in_stock=True).all()
    else:
        products = Product.query.filter_by(in_stock=True).all()
    categories = list(set(p.category for p in Product.query.all()))
    return render_template('shop.html', products=products, categories=categories)

@main.route('/product/<int:id>')
def product(id):
    item = Product.query.get_or_404(id)
    return render_template('product.html', product=item)

@main.route('/cart')
@login_required
def cart():
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('main.login'))

    # --- Récupération sécurisée du panier ---
    cart_data = session.get('cart', {'items': {}, 'shipping_country': 'CIV'})
    if cart_data.get('shipping_country') not in ['CIV', 'International']:
        cart_data['shipping_country'] = 'CIV'

    cart_items = []
    total = 0

    # --- Lecture CORRECTE des articles ---
    for product_id_str, item_data in cart_data['items'].items():
        try:
            product = Product.query.get(int(product_id_str))
            if not product:
                continue

            # ✅ Vérifie que les clés existent
            size = item_data.get('size', 'Non spécifiée')
            color = item_data.get('color', 'Non spécifiée')
            quantity = item_data.get('quantity', 1)

            # Ajoute l'article à la liste
            cart_items.append({
                'product': product,
                'size': size,
                'color': color,
                'quantity': quantity
            })
            total += product.price * quantity

        except (ValueError, TypeError):
            continue

    # --- Calcul livraison (en FCFA) ---
    shipping_country = cart_data['shipping_country']
    shipping = 1500 if shipping_country == 'CIV' else 7500
    total_with_shipping = total + shipping

    # --- Génération du message WhatsApp ---
    order_lines = []
    for item in cart_items:
        line = f"- {item['product'].name} ({item['size']} / {item['color']}) x{item['quantity']}"
        order_lines.append(line)
    
    order_details = "%0A".join(order_lines)  # %0A = saut de ligne

    # ✅ Message complet
    whatsapp_message = (
        "📦 *Nouvelle commande — Confirmation*\n\n"
        "👤 *Informations client*\n"
        f"• Nom : *{user.username}*\n"
        f"• Numéro : *{user.phone or 'Non fourni'}*\n\n"

        "🛍️ *Détails de la commande*\n"
        "💰 *Résumé du paiement*\n"
        f"• Total produits : *{total:,.0f} FCFA*\n"
        f"• Livraison : *{shipping:,.0f} FCFA* "
        f"({ '🇨🇮 Côte d’Ivoire' if shipping_country == 'CIV' else '🌍 International' })\n"
        f"• *Total à payer : {total_with_shipping:,.0f} FCFA*\n\n"

        "Merci 🙏\n"
        "Veuillez confirmer pour finaliser la commande."
    )

    # ✅ Encode UNE SEULE FOIS, proprement
    whatsapp_encoded = urllib.parse.quote(whatsapp_message, safe='')
    print("\n=== DEBUG MESSAGE ===")
    print("Raw message:")
    print(whatsapp_message)
    print("\nEncoded URL:")
    print(f"https://wa.me/2250173324157?text={whatsapp_encoded}")
    print("=== END DEBUG ===\n")

    return render_template(
        'cart.html',
        user=user,
        items=cart_items,  # ← liste d'articles simplifiée
        total=total,
        shipping=shipping,
        shipping_country=cart_data['shipping_country'],
        total_with_shipping=total_with_shipping,
        message=whatsapp_message,
        whatsapp_encoded=whatsapp_encoded
    )

@main.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    
    size = request.form.get('size', 'Non spécifiée')
    color = request.form.get('color', 'Non spécifiée')

    if 'cart' not in session:
        session['cart'] = {'items': {}, 'shipping_country': 'CIV'}

    cart = session['cart']
    pid = str(product_id)

    if pid in cart['items']:
        cart['items'][pid]['quantity'] += 1
    else:
        cart['items'][pid] = {
            'quantity': 1,
            'size': size,
            'color': color
        }

    session['cart'] = cart
    flash(f"{product.name} ajouté au panier.", "success")
    return redirect(url_for('main.cart'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            next_page = request.form.get('next') or url_for('main.cart')
            return redirect(next_page)
        flash("Email ou mot de passe incorrect.", "danger")
    return render_template('login.html', next=request.args.get('next'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form.get('phone', '').strip() or None
        password = request.form['password']
        password2 = request.form['password2']

        if password != password2:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash("Cet email est déjà utilisé.", "danger")
            return render_template('register.html')

        user = User(username=username, email=email, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Compte créé ! Veuillez vous connecter.", "success")
        return redirect(url_for('main.login'))
    return render_template('register.html')


@main.route('/logout')
@login_required
def logout():
    # Supprime les données utilisateur de la session
    session.pop('user_id', None)
    
    # Supprime aussi le panier si tu veux (ou garde-le)
    session.pop('cart', None)
    
    # Message de confirmation (optionnel)
    flash("Vous avez été déconnecté avec succès.", "info")
    
    # Redirige vers la page d'accueil
    return redirect(url_for('main.index'))