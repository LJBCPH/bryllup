import qrcode

# Replace with your actual URL
url = "https://microwave-degree-python-quarter.trycloudflare.com"

# Generate QR code
qr = qrcode.QRCode(
    version=1,  # controls size, 1 is smallest
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# Create an image from the QR Code instance
img = qr.make_image(fill_color="black", back_color="white")

# Save to file
img.save("wedding_app_qrcode.png")

print("QR code saved as 'wedding_app_qrcode.png'.")
