import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import base64
import time

# ===== Konstanta Kunci =====
KEY = 3  # Key sebagai angka

# ===== Caesar Cipher =====
def caesar_encrypt(text, key): 
    result = ''
    for char in text:
        if char.isalpha():
            shift = key % 26
            base = ord('A') if char.isupper() else ord('a') # A= 65, a = 97
            result += chr((ord(char) - base + shift) % 26 + base) # (72 - 65 + 3 = 10) 
        else:
            result += char
    return result

def caesar_decrypt(text, key):
    result = ''
    for char in text:
        if char.isalpha():
            shift = key % 26
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base - shift) % 26 + base) #(68 - 65 - 3= 0)
        else:
            result += char
    return result

# ===== Vigenère Cipher (gunakan key angka) =====
def vigenere_encrypt(text, key):
    result = ''
    key = str(key)  # Konversi key menjadi string jika berupa angka
    key_index = 0
    for char in text:
        if char.isalpha():
            shift = int(key[key_index % len(key)])  # Gunakan digit dari key sebagai pergeseran
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
            key_index += 1
        else:
            result += char
    return result

def vigenere_decrypt(text, key):
    result = ''
    key = str(key)  # Konversi key menjadi string jika berupa angka
    key_index = 0
    for char in text:
        if char.isalpha():
            shift = int(key[key_index % len(key)])  # Gunakan digit dari key sebagai pergeseran
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base - shift) % 26 + base)
            key_index += 1
        else:
            result += char
    return result

# ===== EOF Steganography =====
def encode_eof(image_path, message):
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        encoded_data = image_data + b"\nEOFMSG:" + message.encode()
        encoded_path = f"encoded_image_{int(time.time())}.png"
        with open(encoded_path, "wb") as encoded_file:
            encoded_file.write(encoded_data)
        return encoded_path
    except Exception as e:
        raise e

def decode_eof(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        
        marker = b"\nEOFMSG:"
        if marker in image_data:
            encrypted_message = image_data.split(marker)[-1].decode()
            
            # Dekripsi: Vigenère → Caesar
            decrypted_vigenere = vigenere_decrypt(encrypted_message, KEY)
            key_caesar = KEY  # Gunakan key Caesar yang sudah didefinisikan (angka)
            original_message = caesar_decrypt(decrypted_vigenere, key_caesar)
            return original_message
        else:
            raise ValueError("Tidak ditemukan pesan tersembunyi dalam gambar.")
    except Exception as e:
        raise e

# ===== GUI Function =====
def browse_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        entry_image_path.delete(0, tk.END)
        entry_image_path.insert(0, file_path)

        try:
            img = Image.open(file_path)
            width, height = img.size

            max_dim = 300

            if width > height:
                new_width = max_dim
                new_height = int(height * (max_dim / width))
            else:
                new_height = max_dim
                new_width = int(width * (max_dim / height))

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            image_label.config(image=img_tk)
            image_label.image = img_tk
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat gambar: {str(e)}")

def encode_message():
    image_path = entry_image_path.get()
    message = entry_message.get()

    if not image_path or not message:
        messagebox.showerror("Error", "Lengkapi semua input (gambar dan pesan).")
        return

    try:
        encrypted_caesar = caesar_encrypt(message, KEY)  # Enkripsi dengan Caesar
        encrypted_vigenere = vigenere_encrypt(encrypted_caesar, KEY)  # Enkripsi dengan Vigenère

        encoded_path = encode_eof(image_path, encrypted_vigenere)

        entry_image_path.delete(0, tk.END)
        entry_message.delete(0, tk.END)
        image_label.config(image='')  # Hapus gambar dari UI
        image_label.image = None

        messagebox.showinfo("Success", f"Pesan berhasil disisipkan ke gambar!\n({encoded_path})")
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

def decode_message():
    image_path = entry_image_path.get()

    if not image_path:
        messagebox.showerror("Error", "Pilih gambar yang ingin dibaca pesannya.")
        return

    try:
        decrypted_message = decode_eof(image_path)
        messagebox.showinfo("Pesan Tersembunyi", f"Hasil Dekripsi:\n\n{decrypted_message}")
    except Exception as e:
        messagebox.showerror("Error", f"Gagal mengekstrak atau mendekripsi pesan:\n{str(e)}")

# ===== GUI Setup =====
root = tk.Tk()
root.title("Steganografi EOF - Caesar + Vigenère")
root.geometry("800x600")
root.resizable(False, False)

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill="both", expand=True)

tk.Label(frame, text="Path Gambar:").pack()
entry_image_path = tk.Entry(frame, width=60)
entry_image_path.pack()
tk.Button(frame, text="Browse", command=browse_image).pack(pady=5)

image_label = tk.Label(frame)
image_label.pack(pady=5)

tk.Label(frame, text="Pesan yang akan disisipkan:").pack()
entry_message = tk.Entry(frame, width=60)
entry_message.pack()

tk.Button(frame, text="Sisipkan Pesan", command=encode_message).pack(pady=10)
tk.Button(frame, text="Ekstrak & Dekripsi Pesan", command=decode_message).pack(pady=5)

root.mainloop()
