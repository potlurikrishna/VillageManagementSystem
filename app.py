from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_pymongo import PyMongo
import os
from bson import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb://localhost:27017/villageDB"
app.config['SECRET_KEY'] = os.urandom(24)
mongo = PyMongo(app)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def home():
    return render_template('login.html') 
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        mobile = request.form['mobile']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('signup'))
        
        existing_user = mongo.db.users.find_one({'$or': [{'username': username}, {'mobile': mobile}]})
        if existing_user:
            flash('User already exists', 'danger')
            return redirect(url_for('signup'))
        
        mongo.db.users.insert_one({
            'username': username,
            'mobile': mobile,
            'password': password,  # Store plain text password
            'role': role
        })
        flash('Registration successful', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        session['role'] = role
        session['user_email'] = username
        
        # Find user by username or mobile
        user = mongo.db.users.find_one({'$or': [{'username': username}, {'mobile': username}]})

        if user and user['password'] == password:  # Assuming plain text password for now
            if user['role'] == role.lower():  # Ensure the role matches
                if role.lower() == 'resident':
                    return jsonify({
                        "status": "success",
                        "message": "Login successful!",
                        "redirect_url": url_for('dashboard')  # Redirect URL to resident dashboard
                    })
                elif role.lower() == 'administrator':
                    return jsonify({
                        "status": "success",
                        "message": "Login successful!",
                        "redirect_url": url_for('admin_dashboard')  # Redirect URL to admin dashboard
                    })
            else:
                # Role mismatch
                return jsonify({
                    "status": "error",
                    "message": "Role mismatch! Please select the correct role."
                })
        else:
            # Invalid credentials
            return jsonify({
                "status": "error",
                "message": "Invalid credentials, please try again."
            })
    
    # Render the login page for GET requests
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/newspapers', methods=['GET'])
def show_newspapers():
    newspapers = {
        'Telugu': [
            {'name': 'Eenadu', 'url': 'https://epaper.eenadu.net/', 'description': 'Eenadu is a leading Telugu newspaper providing comprehensive news coverage in Andhra Pradesh and Telangana.'},
            {'name': 'Andhra Jyothy', 'url': 'https://epaper.andhrajyothy.com/', 'description': 'Andhra Jyothy offers extensive news on politics, business, and entertainment from Andhra Pradesh and Telangana.'},
            {'name': 'Andhra Prabha', 'url': 'https://epaper.prabhanews.com/', 'description': 'Andhra Prabha delivers timely updates and in-depth news stories covering a wide range of topics.'},
            {'name': 'Sakshi', 'url': 'https://epaper.sakshi.com/', 'description': 'Sakshi is known for its detailed coverage of local, national, and international news in Telugu.'},
            {'name': 'Vaartha', 'url': 'https://epaper.vaartha.com/', 'description': 'Vaartha provides insightful news and analysis on current events and local affairs.'}
        ],
        'English': [
            {'name': 'The Hindu', 'url': 'https://epaper.thehindu.com/', 'description': 'The Hindu is a major English-language newspaper in India, renowned for its quality journalism and in-depth news coverage.'},
            {'name': 'The Times of India', 'url': 'https://epaper.indiatimes.com/', 'description': 'The Times of India is one of the largest English newspapers in India, offering comprehensive news on various topics.'},
            {'name': 'The Indian Express', 'url': 'https://indianexpress.com', 'description': 'The Indian Express provides detailed reporting on national and international news with a focus on investigative journalism.'},
            {'name': 'Hindustan Times', 'url': 'https://epaper.hindustantimes.com/', 'description': 'Hindustan Times is known for its thorough reporting and coverage of current affairs, politics, and entertainment.'},
            {'name': 'The Economic Times', 'url': 'https://economictimes.indiatimes.com', 'description': 'The Economic Times offers in-depth analysis and news on business, finance, and economic policies.'}
        ]
    }
    return render_template('newspapers.html', newspapers=newspapers)

@app.route('/sarpanch')
def Sarpanch():
    return render_template('sarpanch.html')

@app.route('/MPTC')
def MPTC():
    return render_template('mptc.html')

@app.route('/display')
def display():
    return render_template('display.html')

@app.route('/donation_form')
def donation_form():
    return render_template('donation_form.html')

@app.route('/donor', methods=['GET', 'POST'])
def donor():
    if request.method == 'POST':
        # Extract data from the form
        donor_name = request.form['name']
        donor_email = request.form['email']
        donor_contact = request.form['contact']
        donor_address = request.form['address']
        donation_details = request.form['donation_details']
        donation_amount = request.form['amount']

        # Print the extracted data for debugging
        print(f'Donor Name: {donor_name}')
        print(f'Donor Email: {donor_email}')
        print(f'Donor Contact: {donor_contact}')
        print(f'Donor Address: {donor_address}')
        print(f'Donation Details: {donation_details}')
        print(f'Donation Amount: {donation_amount}')

        # Create a donor dictionary
        donor = {
            'name': donor_name,
            'email': donor_email,
            'contact': donor_contact,
            'address': donor_address,
            'donation_details': donation_details,
            'amount': donation_amount
        }

        # Insert donor data into MongoDB
        mongo.db.donors.insert_one(donor)

        return redirect(url_for('donation_form'))

@app.route('/donation_detail')
def donation_detail():
    donations = mongo.db.donors.find()
    return render_template('donation_detail.html', donations=donations)

@app.route('/wardmember')
def wardmember():
    return render_template('wardmember.html')

@app.route('/population')
def population():
    return render_template('population.html')

@app.route('/availability')
def availability():
    return render_template('availability.html')

@app.route('/complaints')
def complaints():
    return render_template('complaints.html')

@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    if request.method == 'POST':
        # Extract data from the form
        complaint_name = request.form['name']
        complaint_email = request.form['email']
        complaint_contact = request.form['contact']
        complaint_text = request.form['complaint']

        # Create a complaint dictionary
        complaint = {
            'name': complaint_name,
            'email': complaint_email,
            'contact': complaint_contact,
            'complaint': complaint_text
        }

        # Insert complaint data into MongoDB
        mongo.db.complaints.insert_one(complaint)

        return redirect(url_for('thank_you'))  # Redirect to a thank you page after submission

@app.route('/thank_you')
def thank_you():
    return "<h1>Submitted succesfully! We will get back to you soon.</h1>"

@app.route('/development_activities')
def development_activities():
    activities = [
        {"name": "Road Construction", "start_date": "January 15, 2024", "completion": 75},
        {"name": "School Building", "start_date": "March 1, 2024", "completion": 40},
        {"name": "Water Supply Project", "start_date": "February 10, 2024", "completion": 50},
        {"name": "Solar Energy Installation", "start_date": "April 5, 2024", "completion": 20},
    ]
    return render_template('development_activities.html', activities=activities)

@app.route('/water_dept')
def water_dept():
    return render_template('water_dept.html')

@app.route('/electricity')
def electricity():
    return render_template('electricity.html')

@app.route('/tax_dept')
def tax_dept():
    return render_template('tax_dept.html')

@app.route('/agri_dept')
def agri_dept():
    return render_template('agri_dept.html')

@app.route('/certificates')
def certificates():
    return render_template('certificates.html')

@app.route('/income_cert')
def income_cert():
    return render_template('income_cert.html')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/submit_income_cert_application', methods=['POST'])
def submit_income_cert_application():
    if request.method == 'POST':
        # Extract form data
        aadhar_no = request.form['aadhar']  # Aadhar Card No
        student_name = request.form['student_name']  # Student Name
        relation = request.form['relation']  # Relation
        gender = request.form['gender']  # Gender
        dob = request.form['dob']  # Date of Birth
        door_no = request.form['door_no']  # Door No
        locality = request.form['locality']  # Locality/Landmark
        district = request.form['district']  # District
        mandal = request.form['mandal']  # Mandal
        village = request.form['village']  # Village
        pin_code = request.form['pin_code']  # Pin Code
        mobile = request.form['mobile']  # Mobile
        email = request.form['email']  # Email
        income_on_lands = request.form['income_on_lands']  # Income on Lands
        income_on_business = request.form['income_on_business']  # Income on Business
        total_income = request.form['total_income']  # Total Income
        
        # Handle file uploads
        meeseva_application_file = request.files['MeeSeva_Application_Form']
        aadhar_document_file = request.files['Aadhar_doc']

        # Ensure files are uploaded
        if meeseva_application_file and meeseva_application_file.filename.endswith('.pdf'):
            meeseva_file_path = os.path.join(app.config['UPLOAD_FOLDER'], meeseva_application_file.filename)
            meeseva_application_file.save(meeseva_file_path)
        else:
            flash('MeeSeva Application Form must be a PDF file.', 'danger')
            return redirect(url_for('submit_income_cert_application'))

        if aadhar_document_file and aadhar_document_file.filename.endswith('.pdf'):
            aadhar_file_path = os.path.join(app.config['UPLOAD_FOLDER'], aadhar_document_file.filename)
            aadhar_document_file.save(aadhar_file_path)
        else:
            flash('Aadhar Document must be a PDF file.', 'danger')
            return redirect(url_for('submit_income_cert_application'))

        # Create an application dictionary
        application = {
            'AadharCardNo': aadhar_no,
            'StudentName': student_name,
            'Relation': relation,
            'Gender': gender,
            'DateofBirth': dob,
            'PermanentAddress': {
                'Door No': door_no,
                'Locality': locality,
                'District': district,
                'Mandal': mandal,
                'Village': village,
                'Pin Code': pin_code,
            },
            'Mobile': mobile,
            'Email': email,
            'IncomeonLands': income_on_lands,
            'IncomeonBusiness': income_on_business,
            'TotalIncome': total_income,
            'MeeSevaApplicationFormPath': meeseva_file_path,
            'AadharDocumentPath': aadhar_file_path
        }

        # Insert application data into MongoDB
        mongo.db.income_certificate.insert_one(application)

        return redirect(url_for('thank_you'))
    
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/casteApp')
def casteApp():
    return render_template('casteApp.html')

@app.route('/submit_integrated_cert_application', methods=['POST'])
def submit_integrated_cert_application():
    if request.method == 'POST':
        # Extract form data
        aadhar_no = request.form['aadhar']  # Aadhar Card No
        applicant_name = request.form['applicant_name']  # Applicant Name
        relation = request.form['relation']  # Relation
        gender = request.form['gender']  # Gender
        dob = request.form['dob']  # Date of Birth
        
        # Permanent Address
        permanent_address = {
            'door_no': request.form['permanent_door_no'],
            'locality': request.form['permanent_locality'],
            'district': request.form['permanent_district'],
            'mandal': request.form['permanent_mandal'],
            'village': request.form['permanent_village'],
            'secretariat': request.form['permanent_secretariat'],
            'pin_code': request.form['permanent_pin_code']
        }

        # Postal Address
        postal_address = {
            'door_no': request.form['postal_door_no'],
            'locality': request.form['postal_locality'],
            'state': request.form['postal_state'],
            'district': request.form['postal_district'],
            'mandal': request.form['postal_mandal'],
            'village': request.form['postal_village'],
            'pin_code': request.form['postal_pin_code']
        }
        
        mobile = request.form['mobile']  # Mobile
        phone = request.form['phone']  # Phone
        email = request.form['email']  # Email
        remarks = request.form['remarks']  # Remarks
        ration_card_no = request.form['ration_card_no']  # Ration Card No
        delivery_type = request.form['delivery_type']  # Delivery Type

        # Caste Certificate Details
        issued_caste_certificate = request.form['issued_caste_certificate']  # Issued Caste Certificate in Past
        caste_claimed = request.form['caste_claimed']
        caste_category = request.form['caste_category']
        edu_contains_caste = request.form['edu_contains_caste']
        purpose_of_caste_certificate = request.form['purpose_of_caste_certificate']
        religion = request.form['religion']

        # Handle file uploads
        meeseva_application_file = request.files['meeseva_application_form']
        caste_certificate_file = request.files['caste_certificate']
        ssc_marks_memo_file = request.files['ssc_marks_memo']
        study_certificates_file = request.files['study_certificates']
        ration_card_file = request.files['ration_card']
        schedule_file = request.files['schedule']

        uploaded_files = {}

        def save_file(file, file_key):
            if file and file.filename.endswith('.pdf'):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                uploaded_files[file_key] = file_path
            else:
                flash(f'{file_key} must be a PDF file.', 'danger')

        save_file(meeseva_application_file, 'MeeSeva Application Form Path')
        save_file(caste_certificate_file, 'Caste Certificate Path')
        save_file(ssc_marks_memo_file, 'SSC Marks Memo Path')
        save_file(study_certificates_file, 'Study Certificates Path')
        save_file(ration_card_file, 'Ration Card Path')
        save_file(schedule_file, 'Schedule I to IV Path')

        # Create an application dictionary
        application = {
            'AadharCardNo': aadhar_no,
            'ApplicantName': applicant_name,
            'Relation': relation,
            'Gender': gender,
            'DateofBirth': dob,
            'PermanentAddress': permanent_address,
            'PostalAddress': postal_address,
            'Mobile': mobile,
            'Phone': phone,
            'Email': email,
            'Remarks': remarks,
            'RationCardNo': ration_card_no,
            'DeliveryType': delivery_type,
            'CasteCertificateDetails': {
                'IssuedCasteCertificate': issued_caste_certificate,
                'CasteClaimed': caste_claimed,
                'CasteCategory': caste_category,
                'EducationalCertificateContainsCaste': edu_contains_caste,
                'PurposeofCasteCertificate': purpose_of_caste_certificate,
                'Religion': religion
            },
            # Include uploaded file paths
            'Documents': uploaded_files
        }

        # Insert application data into MongoDB
        mongo.db.casteApp.insert_one(application)

        return redirect(url_for('thank_you'))
@app.route('/admin_dashboard')
def admin_dashboard():
    # Fetch complaints and applications from the database
    complaints = list(mongo.db.complaints.find({}))
    casteApp = list(mongo.db.casteApp.find({}))
    income_certificate = list(mongo.db.income_certificate.find({}))
    return render_template(
        'admin_dashboard.html',
        complaints=complaints,
        casteApp=casteApp,
        income_certificate=income_certificate
    )

@app.route('/logout')
def logout():
    return render_template('login.html')

@app.route('/profile')
def profile():
    user_email = session.get('user_email')  # Assuming session stores user's email
    users = mongo.db.users.find_one({"username": user_email})  # Get user details
    donations = mongo.db.donors.find({"email": user_email})  # Filter donations by email
    complaint1 = mongo.db.complaints.find({"email": user_email})  # Filter complaints
    income_certificates = mongo.db.income_certificate.find({"Email": user_email})  # Income certificates
    caste_certificates = mongo.db.casteApp.find({"Email": user_email})  # Caste certificates

    return render_template(
        'profile.html',
        users=users,
        donations=donations,
        complaint1=complaint1,
        income_certificates=income_certificates,
        caste_certificates=caste_certificates
    )
@app.route('/h1')
def h1():
   user_role = session.get('role')
   if user_role == "Resident":
       return render_template('dashboard.html')
   else:
        complaints = list(mongo.db.complaints.find({}))
        casteApp = list(mongo.db.casteApp.find({}))
        income_certificate = list(mongo.db.income_certificate.find({}))
    
        return render_template(
            'admin_dashboard.html',
            complaints=complaints,
            casteApp=casteApp,
            income_certificate=income_certificate
        )
       
       
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        # Fetch form data
        u_n = request.form['username']  # Username acts as the identifier
        mb = request.form.get('mobile')  # New mobile number
        npwd = request.form.get('password')  # New password

        # Check if any data is provided for updating
        if not mb and not npwd:
            error_message = "Please provide at least one field to update."
            return render_template('edit_profile.html', error=error_message)

        # Build the update query
        update_query = {}
        if mb:
            update_query['mobile'] = mb
        if npwd:
            update_query['password'] = npwd

        # Update the user's profile
        result = mongo.db.users.update_one(
            {"username": u_n},  # Find the user by username
            {"$set": update_query}  # Update fields
        )

        # Check if the update was successful
        if result.matched_count > 0:
            success_message = "Profile updated successfully!"
            return render_template('edit_profile.html', success=success_message)
        else:
            error_message = "User not found. Please try again."
            return render_template('edit_profile.html', error=error_message)
    
    # For GET requests, render the edit profile page
    return render_template('edit_profile.html')

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    collection_name = data['collection']  # The collection to update
    status = data['status']  # The new status value
    application_id = data['id']  # The ID of the application/complaint

    # Update the status in the relevant collection
    mongo.db[collection_name].update_one(
        {"_id": ObjectId(application_id)},
        {"$set": {"status": status}}  # Update the status field
    )

    return jsonify({"status": "success", "message": "Status updated successfully"})


if __name__ == '__main__':
    app.run(debug=True)
