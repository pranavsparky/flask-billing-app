from flask import Flask, render_template, request, send_file
from Generate_Bill import generate_bill
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    booking_data = {
        "name": request.form.get('name'),
        "pax": request.form.get('pax'),
        "mobile": request.form.get('mobile'),
        "checkin": request.form.get('checkin'),
        "checkout": request.form.get('checkout'),
        "double_rooms": request.form.get('double_rooms'),
        "double_rent": request.form.get('double_rent'),
        "double_extra": request.form.get('double_extra'),
        "double_ac": request.form.get('double_ac'),
        "triple_rooms": request.form.get('triple_rooms'),
        "triple_rent_per_room": request.form.get('triple_rent_per_room'),
        "triple_extra_bed": request.form.get('triple_extra_bed'),
        "triple_ac": request.form.get('triple_ac'),
        "advance": request.form.get('advance'),
        "discount": request.form.get('discount'),   
        "advance_mode": request.form.get('advance_mode'),
        "total_rent": request.form.get('total_rent'),
        "balance": request.form.get('balance'),
        "remarks": request.form.get('remarks')
    }

    filename = generate_bill(booking_data)
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)  # Changed to True