# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from models import db, User, Product, Supplier, Transaction, Role
from forms import LoginForm, ProductForm, SupplierForm
from helpers import login_required, role_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pandas as pd
from io import BytesIO
from forms import RegisterForm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'tims.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # ✅ utility: seed admin (defined BEFORE usage)
    def seed_admin():
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                role=Role.ADMIN.value
            )
            db.session.add(admin)
            db.session.commit()

    with app.app_context():
        db.create_all()
        seed_admin()

    # ---------------- ROUTES ---------------- #

    @app.route('/')
    def index():
        if session.get('user'):
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET','POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            u = User.query.filter_by(username=form.username.data).first()
            if u and check_password_hash(u.password, form.password.data):
                session['user'] = {'id': u.id, 'username': u.username, 'role': u.role}
                flash(f"Welcome {u.username}", "success")
                return redirect(url_for('dashboard'))
            flash("Invalid username/password", "danger")
        return render_template('login.html', form=form)

    @app.route('/logout')
    def logout():
        session.clear()
        flash("Logged out", "info")
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        total_products = Product.query.count()
        low_stock_count = Product.query.filter(Product.stock <= Product.reorder_point).count()
        out_of_stock = Product.query.filter(Product.stock == 0).count()
        recent_transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(7).all()
        low_stock_products = Product.query.filter(Product.stock <= Product.reorder_point).all()
        return render_template('dashboard.html',
                               total_products=total_products,
                               low_stock_count=low_stock_count,
                               out_of_stock=out_of_stock,
                               transactions=recent_transactions,
                               low_stock_products=low_stock_products)

    # ---------------- Products ---------------- #
    @app.route('/products')
    @login_required
    def products():
        q = request.args.get('q','').strip()
        filter_status = request.args.get('status','')  # low, out
        qs = Product.query
        if q:
            like = f"%{q}%"
            qs = qs.filter((Product.name.ilike(like)) | (Product.code.ilike(like)) | (Product.category.ilike(like)))
        if filter_status == 'low':
            qs = qs.filter(Product.stock <= Product.reorder_point)
        if filter_status == 'out':
            qs = qs.filter(Product.stock == 0)
        products = qs.order_by(Product.name).all()
        return render_template('products.html', products=products, q=q, filter_status=filter_status)

    @app.route('/product/new', methods=['GET','POST'])
    @login_required
    @role_required(['admin','manager'])
    def product_new():
        form = ProductForm()
        suppliers = Supplier.query.all()
        form.supplier_id.choices = [(0,'-- none --')] + [(s.id,s.name) for s in suppliers]
        if form.validate_on_submit():
            supplier_id = form.supplier_id.data or None
            if supplier_id == 0:
                supplier_id = None
            p = Product(code=form.code.data, name=form.name.data, category=form.category.data,
                        stock=form.stock.data or 0, reorder_point=form.reorder_point.data or 0,
                        description=form.description.data, supplier_id=supplier_id)
            db.session.add(p)
            db.session.commit()
            flash("Product added", "success")
            return redirect(url_for('products'))
        return render_template('product_form.html', form=form, action='New')

    @app.route('/product/<int:pid>/edit', methods=['GET','POST'])
    @login_required
    @role_required(['admin','manager'])
    def product_edit(pid):
        p = Product.query.get_or_404(pid)
        form = ProductForm(obj=p)
        suppliers = Supplier.query.all()
        form.supplier_id.choices = [(0,'-- none --')] + [(s.id,s.name) for s in suppliers]
        form.supplier_id.data = p.supplier_id or 0
        if form.validate_on_submit():
            p.code = form.code.data
            p.name = form.name.data
            p.category = form.category.data
            p.stock = form.stock.data or 0
            p.reorder_point = form.reorder_point.data or 0
            p.description = form.description.data
            p.supplier_id = form.supplier_id.data or None
            db.session.commit()
            flash("Product updated", "success")
            return redirect(url_for('products'))
        return render_template('product_form.html', form=form, action='Edit')

    @app.route('/product/<int:pid>/delete', methods=['POST'])
    @login_required
    @role_required(['admin'])
    def product_delete(pid):
        p = Product.query.get_or_404(pid)
        db.session.delete(p)
        db.session.commit()
        flash("Product deleted", "info")
        return redirect(url_for('products'))

    # ---------------- Suppliers ---------------- #
    @app.route('/suppliers')
    @login_required
    def suppliers():
        suppliers = Supplier.query.order_by(Supplier.name).all()
        return render_template('suppliers.html', suppliers=suppliers)

    @app.route('/supplier/new', methods=['GET','POST'])
    @login_required
    @role_required(['admin'])
    def supplier_new():
        form = SupplierForm()
        if form.validate_on_submit():
            s = Supplier(name=form.name.data, contact=form.contact.data,
                         email=form.email.data, address=form.address.data)
            db.session.add(s)
            db.session.commit()
            flash("Supplier added", "success")
            return redirect(url_for('suppliers'))
        return render_template('supplier_form.html', form=form, action='New')

    @app.route('/supplier/<int:sid>/edit', methods=['GET','POST'])
    @login_required
    @role_required(['admin'])
    def supplier_edit(sid):
        s = Supplier.query.get_or_404(sid)
        form = SupplierForm(obj=s)
        if form.validate_on_submit():
            s.name = form.name.data
            s.contact = form.contact.data
            s.email = form.email.data
            s.address = form.address.data
            db.session.commit()
            flash("Supplier updated", "success")
            return redirect(url_for('suppliers'))
        return render_template('supplier_form.html', form=form, action='Edit')

    @app.route('/supplier/<int:sid>/delete', methods=['POST'])
    @login_required
    @role_required(['admin'])
    def supplier_delete(sid):
        s = Supplier.query.get_or_404(sid)
        db.session.delete(s)
        db.session.commit()
        flash("Supplier deleted", "info")
        return redirect(url_for('suppliers'))

    # ---------------- Transactions ---------------- #
    @app.route('/transactions', methods=['GET','POST'])
    @login_required
    def transactions():
        if request.method == 'POST':
            product_id = int(request.form['product_id'])
            ttype = request.form['type']
            qty = int(request.form['qty'])
            notes = request.form.get('notes','')
            supplier_id = request.form.get('supplier_id') or None
            product = Product.query.get_or_404(product_id)
            if ttype == 'out' and product.stock < qty:
                flash("Not enough stock", "danger")
            else:
                if ttype == 'in':
                    product.stock += qty
                else:
                    product.stock -= qty
                tr = Transaction(product_id=product_id, user_id=session['user']['id'],
                                 qty=qty, type=ttype, notes=notes,
                                 supplier_id=supplier_id)
                db.session.add(tr)
                db.session.commit()
                flash("Transaction recorded", "success")
            return redirect(url_for('transactions'))
        products = Product.query.order_by(Product.name).all()
        transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(50).all()
        suppliers = Supplier.query.all()
        return render_template('transactions.html', products=products, transactions=transactions, suppliers=suppliers)
    
    

    @app.route('/register', methods=['GET','POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            if User.query.filter_by(username=form.username.data).first():
                flash("Username already exists", "danger")
            else:
                new_user = User(
                    username=form.username.data,
                    password=generate_password_hash(form.password.data),
                    role=form.role.data
                )
                db.session.add(new_user)
                db.session.commit()
                flash("User registered successfully! Please login.", "success")
                return redirect(url_for('login'))
        return render_template('register.html', form=form)


    # ---------------- CSV Import/Export ---------------- #
    @app.route('/export/products')
    @login_required
    def export_products():
        products = Product.query.all()
        rows = []
        for p in products:
            rows.append({
                'code': p.code, 'name': p.name, 'category': p.category or '',
                'stock': p.stock, 'reorder_point': p.reorder_point or 0,
                'description': p.description or '', 'supplier_id': p.supplier_id or ''
            })
        df = pd.DataFrame(rows)
        buf = BytesIO()
        df.to_csv(buf, index=False)
        buf.seek(0)
        return send_file(buf, mimetype='text/csv', download_name='products.csv', as_attachment=True)

    @app.route('/import/products', methods=['GET','POST'])
    @login_required
    @role_required(['admin','manager'])
    def import_products():
        if request.method == 'POST':
            f = request.files.get('file')
            if not f:
                flash("No file uploaded", "warning")
                return redirect(url_for('import_products'))
            df = pd.read_csv(f)
            count = 0
            for _, row in df.iterrows():
                code = str(row.get('code') or row.get('Code') or '').strip()
                if not code:
                    continue
                p = Product.query.filter_by(code=code).first()
                if not p:
                    p = Product(code=code)
                    db.session.add(p)
                p.name = row.get('name') or row.get('Name') or p.name
                p.category = row.get('category') or row.get('Category') or p.category
                p.stock = int(row.get('stock') or 0)
                p.reorder_point = int(row.get('reorder_point') or 0)
                p.description = row.get('description') or ''
                count += 1
            db.session.commit()
            flash(f"Imported {count} rows", "success")
            return redirect(url_for('products'))
        return render_template('import.html')

    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
