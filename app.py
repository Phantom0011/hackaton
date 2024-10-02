from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask import send_file
from io import BytesIO

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///apartments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Apartment model
class Apartment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    rooms = db.Column(db.Integer, nullable=False, default=1)
    image = db.Column(db.LargeBinary)

    def __repr__(self):
        return f'<Apartment {self.title}>'

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/apartment_image/<int:apartment_id>')
def apartment_image(apartment_id):
    apartment = Apartment.query.get_or_404(apartment_id)
    if apartment.image:
        return send_file(
            BytesIO(apartment.image),
            mimetype='image/jpeg'  # Adjust mimetype if needed
        )
    else:
        return 'No image available', 404


@app.route('/apartments')
def list_apartments():
    apartments = Apartment.query.all()
    return render_template('list_apartments.html', apartments=apartments)

@app.route('/delete_apartment/<int:id>', methods=['POST'])
def delete_apartment(id):
    apartment = Apartment.query.get_or_404(id)
    try:
        db.session.delete(apartment)
        db.session.commit()
        return redirect(url_for('list_apartments'))
    except:
        db.session.rollback()
        return abort(500, description="An error occurred while deleting the apartment.")


@app.route('/add_apartment', methods=['GET', 'POST'])
def add_apartment():
    if request.method == 'POST':
        image_data = request.files.get('image', None)  # Get the uploaded image file
        if image_data:
            image_data = image_data.read()  # Read the image data
            
        new_apartment = Apartment(
            title=request.form.get('title'),
            location=request.form.get('location'),
            price=float(request.form.get('price')),
            bedrooms=int(request.form.get('bedrooms')),
            bathrooms=int(request.form.get('bathrooms')),
            description=request.form.get('description'),
            rooms=int(request.form.get('rooms')),
            image=image_data
        )
        db.session.add(new_apartment)
        db.session.commit()
        return redirect(url_for('list_apartments'))
    return render_template('add_apartment.html')

@app.route('/search', methods=['GET', 'POST'])
def search_apartments():
    if request.method == 'POST':
        location = request.form.get('location', '').strip()
        max_price = request.form.get('max_price', '')
        
        query = Apartment.query

        if location:
            query = query.filter(Apartment.location.ilike(f'%{location}%'))
        
        if max_price:
            try:
                max_price = float(max_price)
                query = query.filter(Apartment.price <= max_price)
            except ValueError:
                return render_template('search_results.html', error="Invalid price input")

        results = query.all()
        return render_template('search_results.html', results=results)
    
    return render_template('search_form.html')

if __name__ == '__main__':
    app.run(debug=True)

from flask import abort

