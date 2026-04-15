#  Secure File Management System

This project is a secure file management system that allows users to upload, store, and download files safely. It ensures data confidentiality and integrity using encryption and authentication mechanisms.

---

##  Features

- User Registration and Login
- Password hashing using bcrypt
- Secure file upload and download
- File encryption using Fernet (cryptography)
- Data integrity check using SHA-256 hashing
- Access control (users can only access their own files)
- Modern UI with dashboard
- Drag and drop file upload
- Upload progress indicator

---

##  Technologies Used

- Python (Flask)
- SQLite
- HTML, CSS, JavaScript
- bcrypt (for password security)
- cryptography (for file encryption)

---

## Security Features

- Passwords are stored in hashed form
- Files are encrypted before storage
- File integrity is verified using hashing
- Secret key is not exposed (protected using .gitignore)

---

##  Project Structure
secure-file-system/
│
├── app.py
├── data.db
├── key.key (ignored)
├── requirements.txt
├── .gitignore
│
├── templates/
│ ├── index.html
│ ├── register.html
│ └── dashboard.html
│
├── uploads/


## How to Run
1. Clone the repository  
2. Install dependencies:
pip install -r requirements.txt


3. Run the application:
python app.py


4. Open in browser:
http://127.0.0.1:5000

##  Note
- The encryption key is generated automatically when the server starts.
- Make sure not to share the key file publicly.

## Author
Shivam Kumar Ojha
