from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import os
import tempfile  # ADDED: For temporary directory

def generate_bill(data):
    # CHANGED: Use temporary directory that works on any server
    target_folder = os.path.join(tempfile.gettempdir(), 'Bookings')
    os.makedirs(target_folder, exist_ok=True) 
    
    # Construct the full path and filename
    base_filename = f"Bill_{data['name'].replace(' ', '_')}.pdf"
    filename = os.path.join(target_folder, base_filename)
    
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Margins and layout
    left_margin = 70
    right_margin = 40
    top_margin = 60
    bottom_margin = 50
    usable_width = width - left_margin - right_margin

    h_title = 18
    h_section = 14
    h_text = 12
    y = height - top_margin

    def new_page():
        nonlocal y
        c.showPage()
        y = height - top_margin

    def ensure_space(needed):
        nonlocal y
        if y - needed < bottom_margin + 50:
            new_page()

    def wrap_and_draw(text, font_name="Helvetica", font_size=12, indent=0):
        """Wrap text within the usable width"""
        nonlocal y
        words = text.split()
        if not words:
            return
        line = ""
        for w in words:
            test = (line + " " + w).strip() if line else w
            test_width = pdfmetrics.stringWidth(test, font_name, font_size)
            if test_width <= usable_width - indent:
                line = test
            else:
                ensure_space(font_size * 1.25)
                c.setFont(font_name, font_size)
                c.drawString(left_margin + indent, y, line)
                y -= font_size * 1.25
                line = w
        if line:
            ensure_space(font_size * 1.25)
            c.setFont(font_name, font_size)
            c.drawString(left_margin + indent, y, line)
            y -= font_size * 1.25

    def start_section(title, font_size=h_section, gap=12):
        """Draw section header"""
        nonlocal y
        y -= gap
        ensure_space(font_size * 1.5)
        c.setFont("Helvetica-Bold", font_size)
        c.drawString(left_margin, y, title)
        y -= font_size * 1.2

    # --- Logo ---
    width, height = A4
    # CHANGED: Use relative path that works on any server
    logo_path = os.path.join(os.path.dirname(__file__), 'static', 'logo.png')
    logo_width, logo_height = 100, 50
    x_center = (width - logo_width) / 2
    
    c.drawImage(logo_path, x_center, y - logo_height, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
    y -= logo_height + 10

    # --- Title (Conditional Logic) ---
    advance_val_str = data.get('advance', '').strip()
    
    try:
        advance_amount = float(advance_val_str)
    except ValueError:
        advance_amount = 0.0
        
    is_advance_paid = advance_amount > 0.0

    if is_advance_paid:
        pdf_title = "BOOKING DETAILS"
    else:
        pdf_title = "BOOKING QUOTATION"
        
    c.setFont("Helvetica-Bold", h_title)
    c.drawCentredString(width / 2, y, pdf_title)
    y -= h_title * 1.5

    # --- Guest Details (Table Format) ---
    start_section("Guest Details")
    guest_table_data = [
        ["Name", data.get('name', '')],
        ["Pax", data.get('pax', '')],
        ["Mobile", data.get('mobile', '')],
        ["Check-in", data.get('checkin', '').replace('T', ' Time ') if data.get('checkin') else ""],
        ["Check-out", data.get('checkout', '').replace('T', ' Time ') if data.get('checkout') else ""]
    ]

    guest_table = Table(guest_table_data, colWidths=[130, 280])
    guest_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.grey)
    ]))
    guest_table.wrapOn(c, width, height)
    table_height = guest_table._height
    ensure_space(table_height + 10)
    guest_table.drawOn(c, left_margin, y - table_height)
    y -= table_height + 10

    # --- Room Details Table ---
    start_section("Room Details")
    table_data = [
        ["Room Type", "No. of Rooms", "Extra Bed", "AC/Non-AC", "Rent"], 
        ["Double Occupancy",
         data.get('double_rooms', ''),
         data.get('double_extra', ''),
         data.get('double_ac', ''),
         data.get('double_rent', '')], 
        ["Triple Occupancy",
         data.get('triple_rooms', ''),
         data.get('triple_extra_bed', ''),
         data.get('triple_ac', ''),
         data.get('triple_rent_per_room', '')]
    ]
    room_table = Table(table_data, colWidths=[150, 80, 70, 80, 60]) 
    room_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    room_table.wrapOn(c, width, height)
    ensure_space(room_table._height + 10)
    room_table.drawOn(c, left_margin, y - room_table._height)
    y -= room_table._height + 10

    # --- Payment Summary (Conditional Logic for Advance field) ---
    start_section("Payment Summary")

    pay_table_data = []
    
    if is_advance_paid:
        pay_table_data.append(["Advance", data.get('advance', '')])
        pay_table_data.append(["Advance Payment Mode", data.get('advance_mode', '')])
    
    kitchen_rent_val = str(data.get('kitchen_rent', '')).strip()
    if kitchen_rent_val and kitchen_rent_val not in ('0', '0.0'):
        pay_table_data.append(["Kitchen Rent", kitchen_rent_val])

    discount_val = str(data.get('discount', '')).strip()
    if discount_val and discount_val not in ('0', '0.0'):
        pay_table_data.append(["Discount", discount_val])

    pay_table_data.extend([
        ["Total Rent", data.get('total_rent', '')],
        ["Balance", data.get('balance', '')],
    ])
    
    if not is_advance_paid:
        pay_table_data = [item for item in pay_table_data if item[0] not in ("Total Rent", "Balance")]
        pay_table_data.extend([
            ["Total Rent", data.get('total_rent', '')],
            ["Balance", data.get('balance', '')],
        ])

    pay_table = Table(pay_table_data, colWidths=[180, 200])
    
    styles = [
        ('BACKGROUND', (0, 0), (-1, -1), colors.aliceblue),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT')
    ]
    
    row_count = len(pay_table_data)
    if row_count >= 2:
        styles.append(('BACKGROUND', (0, row_count-2), (-1, row_count-2), colors.lavender)) 
        styles.append(('BACKGROUND', (0, row_count-1), (-1, row_count-1), colors.mistyrose)) 
        
    pay_table.setStyle(TableStyle(styles))

    pay_table.wrapOn(c, width, height)
    ensure_space(pay_table._height + 10)
    pay_table.drawOn(c, left_margin, y - pay_table._height)
    y -= pay_table._height + 10

    # --- Remarks ---
    remarks = data.get("remarks", "").strip()
    if remarks:
        start_section("Remarks:")
        wrap_and_draw(remarks, font_size=10, indent=8)

    # --- Complimentary Benefits ---
    start_section("Complimentary Benefits")
    wrap_and_draw("The following complimentary items will be provided one time only (per guest) for the entire stay:", font_size=h_text, indent=8)
    benefits = ["Complimentary Water Bottle", "Complimentary Soap", "Complimentary Shampoo", "Complimentary Towel"]
    for item in benefits:
        wrap_and_draw(f"• {item}", font_size=10, indent=20)
    
    # --- Thank You (Centered) ---
    ensure_space(30)
    thank_you_text = "Thank you for booking with us!"
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y - 20, thank_you_text)
    y -= 40 

    # --- Important Terms & Conditions ---
    new_conditional_term = ("Balance Payment Responsibility:", "The above mentioned customer is solely responsible for clearing the full balance amount at the time of check-in.")
    
    terms = [
        ("Quote Validity:", "This quotation is valid for 7 days only. To confirm, we must receive the advance payment within this period."),
        ("Advance Payment Policy:", "A minimum of 30% of the total amount must be paid in advance. This payment is strictly non-refundable, as it reserves the rooms and blocks both online and offline bookings for the specified dates."),
        ("Loss or Damage:", "The management is not liable for any loss, theft or damage to guests personal belongings, valuables or property. Guests are advised to safeguard their items accordingly."),
        ("Alcohol Ban:", "The consumption or possession of alcohol is strictly prohibited within the hotel premises."),
        ("Cleanliness Policy:", "Chewing panmasala or spitting it anywhere inside the premises is forbidden. A penalty of 2,000/- rupees will be charged for each violation."),
        ("Damage Liability:", "Should any damage occur to hotel property (including furniture, fixtures, etc.) during your stay, it will be the responsibility of the individual to whom this quote is addressed. Charges will apply accordingly."),
        ("Power Backup Policy:", "Although the property is equipped with power backup, air conditioning will not operate during power outages. Only essential electrical services such as lights and fans will remain functional."),
        ("Check-out Policy:", "Accommodation is provided for a 24-hour period. Any late check-out will be treated as a full-day stay, and corresponding charges will apply.")
    ]

    if is_advance_paid:
        terms = terms[2:]
        terms.insert(0, new_conditional_term)

    terms_height = len(terms) * 45
    ensure_space(terms_height + 60)
    #c.setFillColor(colors.lightgrey)
    #c.rect(left_margin - 10, y - terms_height - 40, usable_width + 20, terms_height + 60, fill=True, stroke=False)

    c.setFillColor(colors.black)
    start_section("Important Terms & Conditions:", font_size=14, gap=10)

    for title, desc in terms:
        c.setFont("Helvetica-Bold", 12)
        wrap_and_draw(title, font_size=12, indent=8)
        c.setFont("Helvetica", 10)
        wrap_and_draw(desc, font_size=10, indent=20)
        y -= 4

    # --- Signature Block and Address ---
    signature_block_height = 80
    ensure_space(signature_block_height)
    
    address_line_1 = "AA Residency A/C | Contact: 8790057559 | 22-11-246/1, Gollavani Gunta,"
    address_line_2 = "Renigunta Rd, AutoNagar, Tirupati, Andhra Pradesh 517501"
    
    address_y = bottom_margin + 30 
    
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, address_y + 10, address_line_1)
    c.drawCentredString(width / 2, address_y, address_line_2)
    
    c.setLineWidth(0.5)
    c.setStrokeColor(colors.lightgrey)
    c.line(left_margin, address_y + 25, width - right_margin, address_y + 25)
    
    signature_y = address_y + 45
    line_length = 200
    
    c.setStrokeColor(colors.black)
    c.line(left_margin, signature_y, left_margin + line_length, signature_y)
    c.setFont("Helvetica", 10)
    c.drawString(left_margin + 10, signature_y - 12, "Customer Signature")
    
    right_x_start = width - right_margin - line_length
    c.line(right_x_start, signature_y, width - right_margin, signature_y)
    c.setFont("Helvetica", 10)
    c.drawString(right_x_start + 10, signature_y - 12, "Hotel Management Signature")
    
    c.setStrokeColor(colors.lightgrey)
    c.line(left_margin, signature_y + 15, width - right_margin, signature_y + 15)

    c.showPage()
    c.save()
    print(f"\n✅ Booking Bill generated successfully: {filename}\n")
    return filename