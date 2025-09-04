import qrcode

qr = qrcode.QRCode(
    version=2,  # 1 à 40 (taille/complexité du QR code)
    error_correction=qrcode.constants.ERROR_CORRECT_H,  # niveau de correction d’erreur
    box_size=10,  # taille de chaque "case" du QR
    border=4,     # épaisseur de la bordure (en cases)
)

qr.add_data("https://openai.com")
qr.make(fit=True)

img = qr.make_image(fill_color="pink", back_color="white") # couleurs du QR code   
img.save("qrcode.png")

### Avec logo au centre

from PIL import Image

qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
qr.add_data("https://openai.com")
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

logo = Image.open("some_file.png")  # chemin vers le logo
logo = logo.resize((60, 60))    # redimensionner le logo

pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
img.paste(logo, pos)

img.save("qr_with_logo.png")
