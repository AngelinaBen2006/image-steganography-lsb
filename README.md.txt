# Image Steganography using LSB

This project was developed by **Angelina Benny**.  
It aims to enhance data security by enabling users to **hide text messages or files inside images** using the **Least Significant Bit (LSB)** technique.  
The tool features a GUI built with **Tkinter** and supports **user login**, **email sharing**, and both **text** and **file** steganography.

---

## Project Status
✅Completed

---

## Developer Information

| Name           | Email                        |
|----------------|------------------------------|
| Angelina Benny | angelinabenny2006@gmail.com  |

---

## Features

- **Hide Text**: Embed secret messages inside image files.
- **Extract Text**: Retrieve hidden messages using a secret key.
- **Hide Files**: Embed entire files (PDF, ZIP, DOCX, etc.) into images.
- **Extract Files**: Extract hidden files from stego images.
- **Send via Email**: Automatically email the encoded image with key.
- **User Authentication**: Secure login & registration using SQLite.
- GUI with hover effects and image previews.

---

## Technologies Used

- **Python 3**
- **Tkinter** – for GUI
- **Pillow (PIL)** – for image processing
- **SQLite3** – for user management
- **smtplib & email** – for sending emails
- **hashlib** – for password hashing
- **base64 & os** – for encryption support

---

## How It Works

### Text Steganography:
- Converts the message into binary.
- Modifies the least significant bits of pixel values in the image.
- Appends a delimiter (`11111110`) to mark end of message.

### File Steganography:
- Appends the entire file data after the original image bytes.
- Uses a marker (`FILEHIDE\n`) to identify where the hidden file starts.

---

## How to Run Locally

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/image-steganography-lsb.git
   cd image-steganography-lsb

Install required dependencies:

bash
Copy
Edit
pip install pillow
Run the main script:

bash
Copy
Edit
python steganography_gui.py
Login or Register, then explore all features via the GUI.

Project Structure
graphql
Copy
Edit
├── steganography_gui.py           # Main application script
├── project info.html              # HTML page with developer info
├── lock_and_key.webp              # Logo / branding image
├── users.db                       # SQLite user database (auto-created)
├── README.md                      # Project documentation
🛡️ Security Notes
Passwords are hashed with SHA-256 before storing in the database.

Messages are shared via email along with randomly generated keys.

LSB technique is simple but should be combined with encryption for higher-level security in production environments.

License
This project is for academic and educational use.
Contact the developer for permission before reuse in commercial products.

Contact
Have questions or suggestions?
Ping me 
Email: angelinabenny2006@gmail.com