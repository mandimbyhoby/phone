"""
generer_banniere_linkedin.py
Génère une bannière portfolio (1584x396 px — format bannière projet LinkedIn)
avec le QR code du dépôt GitHub, à utiliser dans la section "Featured".

Usage : python generer_banniere_linkedin.py
"""
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont

REPO_URL = "https://github.com/mandimbyhoby/phone"
SORTIE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banniere_linkedin.png")

# Couleurs du site
VIOLET_FONCE = (42, 10, 99)
VIOLET = (109, 25, 255)
BLEU = (29, 92, 244)
ROSE = (208, 0, 255)
OR = (255, 209, 102)
BLANC = (255, 255, 255)


def chercher_police(taille):
    """Cherche une police TTF système."""
    candidats = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        r"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in candidats:
        if os.path.exists(c):
            return ImageFont.truetype(c, taille)
    return ImageFont.load_default()


def main():
    W, H = 1584, 396
    img = Image.new("RGB", (W, H), VIOLET_FONCE)
    draw = ImageDraw.Draw(img)

    # --- Dégradé de fond (bleu → violet → rose) ---
    for x in range(W):
        t = x / W
        if t < 0.5:
            u = t * 2
            r = int(BLEU[0] + (VIOLET[0] - BLEU[0]) * u)
            g = int(BLEU[1] + (VIOLET[1] - BLEU[1]) * u)
            b = int(BLEU[2] + (VIOLET[2] - BLEU[2]) * u)
        else:
            u = (t - 0.5) * 2
            r = int(VIOLET[0] + (ROSE[0] - VIOLET[0]) * u)
            g = int(VIOLET[1] + (ROSE[1] - VIOLET[1]) * u)
            b = int(VIOLET[2] + (ROSE[2] - VIOLET[2]) * u)
        draw.line([(x, 0), (x, H)], fill=(r, g, b))

    # --- Particules décoratives ---
    import random
    random.seed(42)
    for _ in range(90):
        x, y = random.randint(0, W), random.randint(0, H)
        rayon = random.randint(2, 6)
        alpha = random.randint(30, 120)
        couleur = (255, 255, 255, alpha)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([x - rayon, y - rayon, x + rayon, y + rayon], fill=couleur)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    # --- Icône téléphone (dessin simple) ---
    def dessiner_telephone(d, x, y, taille):
        d.rounded_rectangle(
            [x, y, x + taille * 0.62, y + taille], radius=int(taille * 0.14), fill=BLANC
        )
        d.ellipse(
            [x + taille * 0.24, y + taille * 0.9, x + taille * 0.38, y + taille * 0.98],
            fill=VIOLET,
        )
        d.rounded_rectangle(
            [x + taille * 0.1, y + taille * 0.06, x + taille * 0.52, y + taille * 0.5],
            radius=int(taille * 0.06), fill=OR,
        )

    dessiner_telephone(draw, 90, 110, 175)

    # --- QR code (généré vers le repo GitHub) ---
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=3)
    qr.add_data(REPO_URL)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=VIOLET_FONCE, back_color=BLANC).convert("RGB")
    qr_taille = 240
    qr_img = qr_img.resize((qr_taille, qr_taille), Image.LANCZOS)
    qr_x, qr_y = W - qr_taille - 70, (H - qr_taille) // 2
    img.paste(qr_img, (qr_x, qr_y))

    # --- Textes ---
    font_titre = chercher_police(72)
    font_sous = chercher_police(34)
    font_petit = chercher_police(26)

    draw.text((360, 120), "PHONE STORE", font=font_titre, fill=BLANC)
    draw.text((362, 222), "E-commerce Django — Téléphones à Madagascar", font=font_sous, fill=OR)
    draw.text((362, 285), "Python · Django · HTMX · Alpine.js · Stripe · PayPal · Orange Money",
              font=font_petit, fill=(230, 220, 255))

    img.save(SORTIE, "PNG")
    print(f"Bannière générée : {SORTIE} ({img.size[0]}x{img.size[1]} px)")
    print(f"QR code vers : {REPO_URL}")


if __name__ == "__main__":
    main()
