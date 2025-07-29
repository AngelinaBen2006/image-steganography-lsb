try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except ModuleNotFoundError:
    raise ImportError("tkinter is not installed. Please install it or run this script in a GUI-enabled Python environment.")

from PIL import Image, ImageTk
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
import base64
import webbrowser
import sqlite3
import hashlib

# ===================== LSB Text Steganography =====================
def encode_message_in_image(image_path, message):
    image = Image.open(image_path).convert('RGB')
    binary_message = ''.join([format(ord(i), '08b') for i in message]) + '1111111111111110'
    data_index = 0
    pixels = list(image.getdata())

    new_pixels = []
    for pixel in pixels:
        new_pixel = list(pixel)
        for i in range(3): 
            if data_index < len(binary_message):
                new_pixel[i] = (new_pixel[i] & ~1) | int(binary_message[data_index])
                data_index += 1
        new_pixels.append(tuple(new_pixel))

    output_path = os.path.join(os.path.expanduser("~/Downloads"), 'encoded_image.png')
    image.putdata(new_pixels)
    image.save(output_path)
    return output_path

def decode_message_from_image(image_path):
    image = Image.open(image_path).convert('RGB')
    pixels = list(image.getdata())
    binary_data = ''

    for pixel in pixels:
        for color in pixel[:3]:
            binary_data += str(color & 1)

    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    message = ''
    for byte in all_bytes:
        if byte == '11111110':
            break
        message += chr(int(byte, 2))
    return message

# ===================== File Hiding Functions =====================
def hide_file_in_image(image_path, file_path):
    output_path = os.path.join(os.path.expanduser("~/Downloads"), 'image_with_hidden_file.png')
    with open(image_path, 'rb') as img_file, open(file_path, 'rb') as file_to_hide:
        img_data = img_file.read()
        file_data = file_to_hide.read()
    with open(output_path, 'wb') as output:
        output.write(img_data)
        output.write(b'FILEHIDE\n')  # marker
        output.write(file_data)
    return output_path

def extract_file_from_image(stego_image_path, output_file_path):
    with open(stego_image_path, 'rb') as f:
        content = f.read()
        marker_index = content.find(b'FILEHIDE\n')
        if marker_index == -1:
            raise ValueError("No hidden file found.")
        hidden_data = content[marker_index + len(b'FILEHIDE\n'):]
    with open(output_file_path, 'wb') as f:
        f.write(hidden_data)

# ===================== Utilities =====================
def generate_key():
    return base64.b64encode(os.urandom(16)).decode()

def send_email(sender, password, receiver, subject, body, attachment_path):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with open(attachment_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    server.send_message(msg)
    server.quit()

def open_project_info():
    html_path = os.path.abspath("project info.html")
    webbrowser.open(f"file://{html_path}")

# ===================== GUI Hover Effects =====================
def on_enter(e):
    e.widget['background'] = '#1b4f72'

def on_leave(e):
    e.widget['background'] = '#2e86de'

# ===================== GUI Windows =====================
def open_hide_text_window():
    def hide_text():
        path = entry_path.get()
        msg = entry_msg.get()
        sender = entry_sender.get()
        pwd = entry_pwd.get()
        receiver = entry_receiver.get()

        if not all([path, msg, sender, pwd, receiver]):
            messagebox.showerror("Error", "All fields are required.")
            return

        messagebox.showinfo("Encrypting", "Encrypting and sending the image...\nPlease wait.")
        try:
            key = generate_key()
            full_message = f"{msg}\n{key}"
            encoded_path = encode_message_in_image(path, full_message)
            send_email(sender, pwd, receiver, "Encrypted Image", f"Key: {key}", encoded_path)
            messagebox.showinfo("Success", f"\u2705 Image encrypted and emailed!\nSaved at:\n{encoded_path}")
        except Exception as e:
            messagebox.showerror("Failed", f"\u274c {str(e)}")

    win = tk.Toplevel()
    win.title("Hide Text")

    tk.Label(win, text="Image Path").grid(row=0, column=0)
    entry_path = tk.Entry(win, width=50)
    entry_path.grid(row=0, column=1)
    tk.Button(win, text="Browse", command=lambda: entry_path.insert(0, filedialog.askopenfilename())).grid(row=0, column=2)

    tk.Label(win, text="Message").grid(row=1, column=0)
    entry_msg = tk.Entry(win, width=50)
    entry_msg.grid(row=1, column=1, columnspan=2)

    tk.Label(win, text="Sender Email").grid(row=2, column=0)
    entry_sender = tk.Entry(win, width=50)
    entry_sender.grid(row=2, column=1, columnspan=2)

    tk.Label(win, text="SMTP Password").grid(row=3, column=0)
    entry_pwd = tk.Entry(win, width=50, show='*')
    entry_pwd.grid(row=3, column=1, columnspan=2)

    tk.Label(win, text="Receiver Email").grid(row=4, column=0)
    entry_receiver = tk.Entry(win, width=50)
    entry_receiver.grid(row=4, column=1, columnspan=2)

    hide_btn = tk.Button(win, text="Hide Text", command=hide_text, bg='#2e86de', fg='white')
    hide_btn.grid(row=5, column=1, pady=10)
    hide_btn.bind("<Enter>", on_enter)
    hide_btn.bind("<Leave>", on_leave)

def open_extract_text_window():
    def extract():
        path = entry_path.get()
        password = entry_pwd.get()
        if not path or not password:
            messagebox.showerror("Error", "Both fields are required.")
            return
        msg = decode_message_from_image(path)
        if password in msg:
            messagebox.showinfo("Extracted Message", msg.replace(password, ''))
        else:
            messagebox.showerror("Error", "Incorrect password or message not found.")

    win = tk.Toplevel()
    win.title("Extract Text")

    tk.Label(win, text="Image Path").grid(row=0, column=0)
    entry_path = tk.Entry(win, width=50)
    entry_path.grid(row=0, column=1)
    tk.Button(win, text="Browse", command=lambda: entry_path.insert(0, filedialog.askopenfilename())).grid(row=0, column=2)

    tk.Label(win, text="Password").grid(row=1, column=0)
    entry_pwd = tk.Entry(win, width=50, show='*')
    entry_pwd.grid(row=1, column=1, columnspan=2)

    extract_btn = tk.Button(win, text="Extract Text", command=extract, bg='#2e86de', fg='white')
    extract_btn.grid(row=2, column=1, pady=10)
    extract_btn.bind("<Enter>", on_enter)
    extract_btn.bind("<Leave>", on_leave)

def open_file_hide_window():
    def hide_file():
        img_path = entry_img.get()
        file_path = entry_file.get()

        if not img_path or not file_path:
            messagebox.showerror("Error", "Both paths required.")
            return

        try:
            stego_path = hide_file_in_image(img_path, file_path)
            messagebox.showinfo("Success", f"File hidden in image:\n{stego_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    win = tk.Toplevel()
    win.title("Hide File in Image")

    tk.Label(win, text="Image Path").grid(row=0, column=0)
    entry_img = tk.Entry(win, width=50)
    entry_img.grid(row=0, column=1)
    tk.Button(win, text="Browse", command=lambda: entry_img.insert(0, filedialog.askopenfilename())).grid(row=0, column=2)

    tk.Label(win, text="File to Hide").grid(row=1, column=0)
    entry_file = tk.Entry(win, width=50)
    entry_file.grid(row=1, column=1)
    tk.Button(win, text="Browse", command=lambda: entry_file.insert(0, filedialog.askopenfilename())).grid(row=1, column=2)

    file_btn = tk.Button(win, text="Hide File", command=hide_file, bg='#2e86de', fg='white')
    file_btn.grid(row=2, column=1, pady=10)
    file_btn.bind("<Enter>", on_enter)
    file_btn.bind("<Leave>", on_leave)

def open_file_extract_window():
    def extract_file():
        stego_path = entry_stego.get()
        output_path = filedialog.asksaveasfilename(title="Save Extracted File As")

        if not stego_path or not output_path:
            messagebox.showerror("Error", "Both fields are required.")
            return

        try:
            extract_file_from_image(stego_path, output_path)
            messagebox.showinfo("Success", f"📁 File extracted and saved at:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Failed", f"❌ Something went wrong:\n{str(e)}")

    win = tk.Toplevel()
    win.title("Extract File from Image")

    tk.Label(win, text="Stego Image Path").grid(row=0, column=0)
    entry_stego = tk.Entry(win, width=50)
    entry_stego.grid(row=0, column=1)
    tk.Button(win, text="Browse", command=lambda: entry_stego.insert(0, filedialog.askopenfilename())).grid(row=0, column=2)

    extract_btn = tk.Button(win, text="Extract File", command=extract_file, bg='#2e86de', fg='white')
    extract_btn.grid(row=1, column=1, pady=10)
    extract_btn.bind("<Enter>", on_enter)
    extract_btn.bind("<Leave>", on_leave)

# ===================== USER DATABASE =====================
def create_user_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def validate_login(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == hash_password(password)


def show_login_window():
    login = tk.Tk()
    login.title("Login")
    login.geometry("300x200")
    login.configure(bg='#1e1e1e')

    tk.Label(login, text="Username", bg='#1e1e1e', fg='white' ).pack()
    username_entry = tk.Entry(login)
    username_entry.pack()

    tk.Label(login, text="Password", bg='#1e1e1e', fg='white').pack()
    password_entry = tk.Entry(login, show="*")
    password_entry.pack()

    def attempt_login():
        user = username_entry.get()
        pwd = password_entry.get()
        if validate_login(user, pwd):
            login.destroy()
            start_main_gui()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def open_register():
        login.destroy()
        show_register_window()

    tk.Button(login, text="Login", command=attempt_login, bg='#2e86de', fg='white').pack(pady=5)
    tk.Button(login, text="Register", command=open_register, bg='#2e86de', fg='white').pack()

    login.mainloop()

def show_register_window():
    reg = tk.Tk()
    reg.title("Register")
    reg.geometry("300x200")

    tk.Label(reg, text="New Username", bg='#1e1e1e', fg='white').pack()
    username_entry = tk.Entry(reg)
    username_entry.pack()

    tk.Label(reg, text="New Password", bg='#1e1e1e', fg='white').pack()
    password_entry = tk.Entry(reg, show="*")
    password_entry.pack()

    def attempt_register():
        user = username_entry.get()
        pwd = password_entry.get()
        if register_user(user, pwd):
            messagebox.showinfo("Success", "Registration successful!")
            reg.destroy()
            show_login_window()
        else:
            messagebox.showerror("Error", "Username already exists.")

    tk.Button(reg, text="Register", command=attempt_register, bg='#2e86de', fg='white').pack(pady=5)
    tk.Button(reg, text="Back to Login", command=lambda: [reg.destroy(), show_login_window()], bg='#2e86de', fg='white').pack()

    reg.mainloop()



# ===================== Main App Window =====================
def start_main_gui():
    root = tk.Tk()
    root.title("Image Steganography Tool")
    root.geometry("400x450")
    root.configure(bg='#1e1e1e')

    tk.Label(root, text="IMAGE STEGANOGRAPHY TOOL", font=('Helvetica', 14, 'bold'), fg='white', bg='#1e1e1e').pack(pady=10)

    tk.Button(root, text="Hide Text", command=open_hide_text_window, bg='blue',fg='white', width=20).pack(pady=5)
    tk.Button(root, text="Extract Text", command=open_extract_text_window, bg='blue', fg='white',width=20).pack(pady=5)
    tk.Button(root, text="Hide File", command=open_file_hide_window, bg='blue', fg='white', width=20).pack(pady=5)
    tk.Button(root, text="Extract File", command=open_file_extract_window, bg='blue', fg='white', width=20).pack(pady=5)
    image_path = "lock_and_key.webp"  
    if os.path.exists(image_path):
        loaded_img = Image.open(image_path)
        resized_img = loaded_img.resize((120, 120))  
        tk_img = ImageTk.PhotoImage(resized_img)

        img_label = tk.Label(root, image=tk_img, bg='black')
        img_label.image = tk_img  # Prevent garbage collection
        img_label.pack(pady=10)
    else:
        print(f"Image not found at {image_path}")

    tk.Button(root, text="Project Info", command=open_project_info, bg='blue', fg='white', width=20).pack(pady=20)

# Start app
create_user_table()
show_login_window()

