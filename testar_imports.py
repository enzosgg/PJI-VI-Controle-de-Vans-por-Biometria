print("Testando importações...")

try:
    import django
    print(f"✓ Django {django.get_version()}")
except:
    print("✗ Django não instalado")

try:
    import cv2
    print(f"✓ OpenCV {cv2.__version__}")
except:
    print("✗ OpenCV não instalado")

try:
    import mediapipe as mp
    print(f"✓ MediaPipe instalado")
except:
    print("✗ MediaPipe não instalado")

try:
    import qrcode
    print(f"✓ QRCode instalado")
except:
    print("✗ QRCode não instalado")

try:
    import PIL
    print(f"✓ Pillow {PIL.__version__}")
except:
    print("✗ Pillow não instalado")

print("\nTeste concluído!")