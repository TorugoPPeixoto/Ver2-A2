import sys
from pathlib import Path
from datetime import datetime
import cv2

# Adiciona o diretório do backend para importar o módulo de descriptografia
base_dir = Path(__file__).resolve().parent.parent
backend_dir = base_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from utils.AES256 import decrypt

def decode_qr(image_path: Path):
    if not image_path.exists():
        print(f"[ERRO] Imagem não encontrada: {image_path}")
        return

    # 1. Carrega a imagem
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"[ERRO] Não foi possível ler a imagem: {image_path}")
        return

    # 2. Adiciona uma margem branca (quiet zone) caso o QR Code esteja cortado rente
    img_bordered = cv2.copyMakeBorder(img, 30, 30, 30, 30, cv2.BORDER_CONSTANT, value=[255, 255, 255])

    # 3. Detecta e decodifica o QR Code usando OpenCV
    detector = cv2.QRCodeDetector()
    qr_text, points, _ = detector.detectAndDecode(img_bordered)

    if not qr_text:
        # Tenta na imagem original sem borda adicional
        qr_text, points, _ = detector.detectAndDecode(img)

    if not qr_text:
        print("[AVISO] Nenhum QR Code detectado na imagem.")
        return

    print("=" * 50)
    print("           LEITURA DO QR CODE")
    print("=" * 50)
    print(f"Texto lido do QR Code: {qr_text}")
    print(f"Tamanho do texto lido: {len(qr_text)} caracteres")

    # 4. Descriptografia dos dados (AES-256-ECB)
    try:
        data_bytes = bytes.fromhex(qr_text)
        decrypted = decrypt(data_bytes)

        if len(decrypted) >= 16:
            cpf = int.from_bytes(decrypted[0:8], byteorder="big")
            ts_start = int.from_bytes(decrypted[8:12], byteorder="big")
            ts_end = int.from_bytes(decrypted[12:16], byteorder="big")

            dt_start = datetime.fromtimestamp(ts_start)
            dt_end = datetime.fromtimestamp(ts_end)
            now = datetime.now()

            is_valid = dt_start <= now <= dt_end

            print("\n" + "=" * 50)
            print("         DADOS DESCRIPTOGRAFADOS")
            print("=" * 50)
            print(f"CPF:           {str(cpf).zfill(11)}")
            print(f"Data Inicial:  {dt_start.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"Data Final:    {dt_end.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"Status Atual:  {'LIBERADO (VÁLIDO)' if is_valid else 'EXPIRADO / FORA DO HORÁRIO'}")
            print("=" * 50)
        else:
            print(f"[AVISO] Bytes descriptografados insuficientes ({len(decrypted)} bytes)")
    except Exception as e:
        print(f"[ERRO ao descriptografar]: {e}")

if __name__ == "__main__":
    # Caminho padrão para image.png
    default_img = base_dir / "image.png"
    target_img = Path(sys.argv[1]) if len(sys.argv) > 1 else default_img
    decode_qr(target_img)
