import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio

W, H, FPS = 1080, 1920, 30
DUR = 92.92
N = int(DUR * FPS)
BN = "/tmp/NotoSansBengali-VF.ttf"

def bfont(size):
    f = ImageFont.truetype(BN, size)
    try: f.set_variation_by_axes([100, 700])
    except Exception: pass
    return f

def wrap(lines, f, maxw=960):
    out = []
    for ln in lines:
        d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
        words, cur = ln.split(), ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= maxw: cur = t
            else: out.append(cur); cur = w
        out.append(cur)
    return out

def text_sprite(lines, size=58, accent_idx=None):
    f = bfont(size)
    lines = wrap(lines, f)
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    lh = int(size * 1.75)
    wmax = max(int(d.textlength(l, font=f)) for l in lines)
    img = Image.new("RGBA", (wmax + 40, lh * len(lines) + 40), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        col = (250, 204, 21, 255) if accent_idx is not None and i in accent_idx else (255, 255, 255, 255)
        lw = int(dr.textlength(l, font=f))
        dr.text(((img.width - lw) / 2, 20 + i * lh), l, font=f, fill=col)
    return np.asarray(img)

def paste(frame, spr, x, y, alpha=1.0):
    h, w = spr.shape[:2]
    x, y = int(x), int(y)
    if x <= -w or x >= W or y <= -h or y >= H: return
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    s = spr[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32)
    a = (s[..., 3:4] / 255.0) * alpha
    frame[y0:y1, x0:x1] = (s[..., :3] * a + frame[y0:y1, x0:x1] * (1 - a)).astype(np.uint8)

def umbrella(color, dark_stroke):
    img = Image.new("RGBA", (560, 620), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.pieslice([30, 40, 530, 540], 180, 360, fill=color, outline=dark_stroke, width=6)
    for ang in (210, 240, 270, 300, 330):
        a = math.radians(ang)
        d.line([(280, 290), (280 + 250 * math.cos(a), 290 + 250 * math.sin(a))], fill=dark_stroke, width=4)
    d.line([(280, 290), (280, 560)], fill=dark_stroke, width=10)
    d.arc([280 - 45, 560 - 45, 280 + 45, 560 + 45], 0, 180, fill=dark_stroke, width=10)
    return np.asarray(img)

# scenes: (start, end, lines, accent lines, umbrella: None/'black'/'red', rain intensity, quote)
SCENES = [
    (0.00,  6.12,  ["ভালোবাসার ছাতা"], None, "black", 0.5, False, 84),
    (6.12,  13.23, ["আমাদের গ্রামের স্কুল|বাড়ি থেকে তিন মাইল দূরে|বর্ষাকালে পথ কাদায় ডুবে যেত"], None, None, 0.8, False, 56),
    (13.23, 20.12, ["বাবার ছিল একটা|পুরনো কালো ছাতা|তিনটা শিক ভাঙা|সেলাইয়ের পর সেলাই"], None, "black", 0.6, False, 56),
    (20.12, 25.98, ["রোজ সকালে বাবা ছাতাটা|আমার হাতে ধরিয়ে দিতেন|নিজে মাথায় গামছা জড়িয়ে|মাঠে চলে যেতেন"], None, "black", 0.7, False, 54),
    (25.98, 32.94, ["খুব লজ্জা লাগত|বন্ধুদের ছাতা কত রঙিন|আমারটা দেখে সবাই হাসত"], None, "black", 0.6, False, 56),
    (32.94, 40.51, ["বাবা, আমি আর এই ছাতা নিয়ে|স্কুলে যাব না"], {0, 1}, None, 0.7, True, 64),
    (40.51, 46.75, ["বাবা কিছু বললেন না|শুধু একটু হেসে|মাথা নিচু করলেন"], None, None, 0.6, False, 56),
    (46.75, 52.78, ["পরদিন ভোরে ঘুম ভেঙে দেখি|বাবা ঘরে নেই|বাইরে মুষলধারে বৃষ্টি"], {2}, None, 1.0, False, 56),
    (52.78, 60.46, ["দুপুরে বাবা ভিজে একাকার|হাতে নতুন লাল ছাতা|মাথায় সেই গামছা — তখনও ভেজা"], {1}, "red", 0.8, False, 54),
    (60.46, 67.26, ["তিন মাইল হেঁটে বাজারে|গিয়েছিলাম রে মা|ধান বিক্রির টাকা|একটু জমিয়েছিলাম"], None, None, 0.5, True, 56),
    (67.26, 73.37, ["বাবার পায়ের জুতো|ছিঁড়ে গেছে|তবু নিজের জন্য|কিছু কেনেননি"], None, None, 0.5, False, 56),
    (73.37, 79.47, ["সেদিন প্রথম বুঝলাম|ছাতা ভাঙা ছিল না|ভালোবাসা ছিল|প্রতিটা সেলাইয়ে"], {1, 2}, None, 0.5, False, 58),
    (79.47, 87.18, ["আজ আলমারিতে অনেক|দামি ছাতা আছে|তবু যত্নে রাখা আছে|সেই কালো ছাতাটা"], {3}, "black", 0.4, False, 54),
    (87.18, 92.92, ["কিছু ভালোবাসা আছে|যা বৃষ্টিতে ভিজে না|কেবল মনটাকে|ভিজিয়ে দেয়"], None, None, 0.6, False, 58),
]

# precompute sprites
for i, s in enumerate(SCENES):
    lines = s[2] if isinstance(s[2], list) else s[2].split("|")
    acc = s[3]
    SCENES[i] = s[:2] + (text_sprite(lines, s[7], acc),) + s[3:7]

umb_black = umbrella((25, 25, 35, 255), (90, 90, 110, 255))
umb_red   = umbrella((200, 40, 50, 255), (120, 20, 25, 255))

# static bg: dark rainy gradient + vignette
top = np.array([14, 16, 30], np.float32); bot = np.array([38, 44, 78], np.float32)
rows = np.linspace(0, 1, H)[:, None]
grad = (top * (1 - rows) + bot * rows).astype(np.uint8)
BG = np.tile(grad[:, None, :], (1, W, 1))
yy, xx = np.mgrid[0:H, 0:W]
vig = 1 - 0.45 * (((xx - W/2) / (W/2))**2 + ((yy - H/2) / (H/2))**2).clip(0, 1)[..., None]
BG = (BG * vig).astype(np.uint8)

# rain layer (tile larger than frame, scrolled diagonally)
random.seed(11)
RW, RH = W + 300, H + 500
rain = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
dr = ImageDraw.Draw(rain)
for _ in range(150):
    x, y = random.uniform(0, RW), random.uniform(0, RH)
    ln = random.uniform(50, 130)
    dr.line([(x, y), (x - ln * 0.28, y + ln)], fill=(170, 190, 230, random.randint(60, 130)), width=2)
RAIN = np.asarray(rain)

writer = imageio.get_writer("/tmp/story/story.mp4", fps=FPS, codec="libx264", quality=7,
                            macro_block_size=1, output_params=["-pix_fmt", "yuv420p"])

def scene_at(t):
    for i, s in enumerate(SCENES):
        if s[0] <= t < s[1]: return i
    return len(SCENES) - 1

for n in range(N):
    t = n / FPS
    frame = BG.copy()
    si = scene_at(t)
    sc = SCENES[si]
    # rain scroll, intensity eases between scenes
    inten = sc[6]
    off_y = int((t * 900 * inten) % RH)
    off_x = int((t * 250 * inten) % RW)
    rows_i = (np.arange(H) + (RH - off_y - H)) % RH
    cols_i = (np.arange(W) + (RW - off_x - W)) % RW
    tile = RAIN[rows_i][:, cols_i]
    a = (tile[..., 3:4].astype(np.float32) / 255.0) * min(1.0, inten)
    frame = (tile[..., :3].astype(np.float32) * a + frame * (1 - a)).astype(np.uint8)
    # lightning in scene 8
    if si == 7:
        for lt in (48.3, 50.9):
            if abs(t - lt) < 0.12:
                frame = (frame * 0.55 + np.full_like(frame, 200) * 0.45).astype(np.uint8)
    # umbrella
    umb = sc[4]
    if umb:
        spr = umb_black if umb == "black" else umb_red
        st, en = sc[0], sc[1]
        k = min(1.0, (t - st) / 0.9)
        k = 1 - (1 - k) ** 3
        fade = min(1.0, (en - t) / 0.5)
        scale = 0.8 + 0.2 * k
        sw = int(spr.shape[1] * scale); sh = int(spr.shape[0] * scale)
        if sw > 0 and sh > 0:
            rs = np.asarray(Image.fromarray(spr).resize((sw, sh), Image.LANCZOS))
            sway = 14 * math.sin(t * 1.4)
            paste(frame, rs, (W - sw) / 2 + sway, 1350 - sh / 2 + (1 - k) * 120, alpha=fade * 0.95)
    # text
    spr = sc[2]
    st, en = sc[0], sc[1]
    kin = min(1.0, (t - st) / 0.7)
    kin = 1 - (1 - kin) ** 3
    fout = min(1.0, (en - t) / 0.45)
    paste(frame, spr, (W - spr.shape[1]) / 2, 420 + (1 - kin) * 70, alpha=kin * fout)
    # title glow on scene 1
    if si == 0:
        glow = 0.5 + 0.5 * math.sin(t * 2)
        paste(frame, spr, (W - spr.shape[1]) / 2, 420, alpha=0.25 * glow)
    writer.append_data(frame)

writer.close()
print("rendered", N, "frames")
