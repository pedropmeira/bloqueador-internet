from PIL import Image, ImageDraw, ImageFont
import math, os

def criar_icone():
    sizes = [256, 128, 64, 48, 32, 16]
    frames = []

    for size in sizes:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        s = size

        # Fundo circular gradiente simulado (círculo escuro)
        margin = int(s * 0.04)
        draw.ellipse([margin, margin, s - margin, s - margin],
                     fill='#0d1117')

        # Anel externo sutil
        draw.ellipse([margin, margin, s - margin, s - margin],
                     outline='#30363d', width=max(1, int(s * 0.018)))

        # Escudo — pontos relativos ao tamanho
        cx = s / 2
        sh_top  = s * 0.15
        sh_bot  = s * 0.85
        sh_left = s * 0.22
        sh_right= s * 0.78
        sh_mid  = s * 0.55   # onde começa a ponta

        shield = [
            (cx,      sh_top),
            (sh_right,sh_top + s * 0.08),
            (sh_right,sh_mid),
            (cx,      sh_bot),
            (sh_left, sh_mid),
            (sh_left, sh_top + s * 0.08),
        ]
        draw.polygon(shield, fill='#cf222e')

        # Brilho interno do escudo
        inner_margin = s * 0.055
        shield_inner = [
            (cx,                  sh_top + inner_margin),
            (sh_right - inner_margin, sh_top + s * 0.08 + inner_margin * 0.5),
            (sh_right - inner_margin, sh_mid - inner_margin * 0.3),
            (cx,                  sh_bot - inner_margin * 1.4),
            (sh_left + inner_margin,  sh_mid - inner_margin * 0.3),
            (sh_left + inner_margin,  sh_top + s * 0.08 + inner_margin * 0.5),
        ]
        draw.polygon(shield_inner, fill='#e74c3c')

        # Cadeado no centro do escudo
        lk_w  = s * 0.22
        lk_h  = s * 0.17
        lk_x  = cx - lk_w / 2
        lk_y  = s * 0.46
        lk_r  = int(s * 0.04)

        # Corpo do cadeado
        draw.rounded_rectangle([lk_x, lk_y, lk_x + lk_w, lk_y + lk_h],
                                radius=lk_r, fill='#0d1117')

        # Arco do cadeado
        arc_w = lk_w * 0.55
        arc_x = cx - arc_w / 2
        arc_t = lk_y - lk_h * 0.68
        arc_b = lk_y + lk_h * 0.18
        arc_thick = max(2, int(s * 0.045))
        draw.arc([arc_x, arc_t, arc_x + arc_w, arc_b],
                 start=180, end=0, fill='#0d1117', width=arc_thick)

        # Buraco da chave
        kh_r = max(2, int(s * 0.035))
        draw.ellipse([cx - kh_r, lk_y + lk_h * 0.28 - kh_r,
                      cx + kh_r, lk_y + lk_h * 0.28 + kh_r],
                     fill='#cf222e')
        draw.rectangle([cx - kh_r * 0.5, lk_y + lk_h * 0.28,
                        cx + kh_r * 0.5, lk_y + lk_h * 0.72],
                       fill='#cf222e')

        frames.append(img)

    out = os.path.join(os.path.dirname(__file__), 'icon.ico')
    frames[0].save(out, format='ICO', sizes=[(s, s) for s in sizes],
                   append_images=frames[1:])
    print(f"Ícone salvo em: {out}")

criar_icone()
