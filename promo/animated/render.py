import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio

W, H, FPS = 1080, 1920, 30
FONT_DIR = "/home/appuser/.local/lib/python3.12/site-packages/matplotlib/mpl-data/fonts/ttf/"

def font(size, bold=True):
    return ImageFont.truetype(FONT_DIR + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)

def sprite(text, f, fill=(255,255,255,255)):
    d = ImageDraw.Draw(Image.new("RGBA", (10,10)))
    w = int(d.textlength(text, font=f)); h = f.size + 40
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    ImageDraw.Draw(img).text((0, 10), text, font=f, fill=fill)
    return np.asarray(img)

def paste(frame, spr, x, y):
    h, w = spr.shape[:2]
    x, y = int(x), int(y)
    if x <= -w or x >= W or y <= -h or y >= H: return
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    sx0, sy0 = x0 - x, y0 - y
    s = spr[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
    a = s[..., 3:4].astype(np.float32) / 255.0
    frame[y0:y1, x0:x1] = (s[..., :3] * a + frame[y0:y1, x0:x1] * (1 - a)).astype(np.uint8)

def ease_out_cubic(t): return 1 - (1 - t) ** 3
def ease_out_back(t):
    c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

# timeline (seconds)
D = 18.0
N = int(D * FPS)

PRIMARY = (79, 70, 229); ACCENT = (250, 204, 21); WHITE = (255, 255, 255)

# sprites
sp_rd       = sprite("RD", font(300), WHITE + (255,))
sp_solution = sprite("SOLUTION", font(130), WHITE + (255,))
sp_sub      = sprite("Mobile Hardware & Repair", font(52, False), ACCENT + (255,))
services    = ["Screen Replacement", "Battery Change", "Charging Port", "Water Damage Fix", "Software Flash"]
sp_srv      = [sprite(s, font(58, False), WHITE + (255,)) for s in services]
sp_why      = sprite("Why RD Solution?", font(84), ACCENT + (255,))
reasons     = ["Expert Technicians", "Genuine Parts", "Fast Service", "Fair Price"]
sp_rsn      = [sprite("✓  " + r, font(56, False), WHITE + (255,)) for r in reasons]
sp_tag1     = sprite("Your Phone,", font(92), WHITE + (255,))
sp_tag2     = sprite("Our Responsibility", font(92), WHITE + (255,))
sp_contact  = sprite("Contact Us Today", font(96), ACCENT + (255,))
sp_phone    = sprite("Call / WhatsApp", font(64, False), WHITE + (255,))

# particles (drift upward)
random.seed(7)
parts = [{"x": random.uniform(0, W), "y": random.uniform(0, H), "r": random.randint(3, 9),
          "v": random.uniform(18, 55), "a": random.randint(28, 70)} for _ in range(45)]
dot = sprite("●", font(30), (255, 255, 255, 255))

def bg(t):
    # animated gradient dark navy -> indigo, slow wave
    k = 0.5 + 0.5 * math.sin(t * 0.35)
    top = np.array([18, 18, 38]); bot = np.array(PRIMARY)
    col = (top * (1 - k) + bot * k).astype(np.float32)
    rows = np.linspace(0, 1, H)[:, None]
    grad = (col * (1 - rows) + bot[None, :] * rows).astype(np.uint8)
    return np.tile(grad[:, None, :], (1, W, 1))

writer = imageio.get_writer("/tmp/rd2/rd_intro.mp4", fps=FPS, codec="libx264", quality=8,
                            macro_block_size=1, output_params=["-pix_fmt", "yuv420p"])

for n in range(N):
    t = n / FPS
    frame = bg(t)
    # particles
    for p in parts:
        py = (p["y"] - p["v"] * t) % (H + 60) - 30
        px = (p["x"] + 12 * math.sin(t + p["r"])) % W
        paste(frame, dot, px, py)
    # vertical accent line sweep
    line = sprite("|", font(200), ACCENT + (255,))
    if t < 1.2:
        paste(frame, line, W/2 - 25, -80 + ease_out_cubic(min(1, t/1.2)) * 120)

    # scene 1: RD slides from left, SOLUTION from right (0.4-2.2s)
    if 0.4 <= t < 6.0:
        k = ease_out_back(min(1, max(0, (t - 0.4) / 1.2)))
        paste(frame, sp_rd, -sp_rd.shape[1] + k * (W/2 - sp_rd.shape[1]/2 + sp_rd.shape[1]), 620)
        k2 = ease_out_back(min(1, max(0, (t - 0.8) / 1.2)))
        paste(frame, sp_solution, W - k2 * (W/2 + sp_solution.shape[1]/2), 980)
        k3 = ease_out_cubic(min(1, max(0, (t - 1.6) / 0.8)))
        paste(frame, sp_sub, (W - sp_sub.shape[1])/2, 1250 + (1 - k3) * 80)
    # scene 2: services slide in from right (5.2-9.8s)
    if 5.2 <= t < 10.2:
        for i, s in enumerate(sp_srv):
            st = 5.4 + i * 0.55
            k = ease_out_cubic(min(1, max(0, (t - st) / 0.7)))
            paste(frame, s, (W - s.shape[1]) / 2 + (1 - k) * 300, 430 + i * 150)
    # scene 3: why + reasons pop (9.6-13.6s)
    if 9.6 <= t < 14.0:
        k = ease_out_back(min(1, max(0, (t - 9.7) / 0.7)))
        paste(frame, sp_why, (W - sp_why.shape[1])/2, 380 + (1 - k) * -120)
        for i, s in enumerate(sp_rsn):
            st = 10.2 + i * 0.5
            k = ease_out_back(min(1, max(0, (t - st) / 0.6)))
            paste(frame, s, (W - s.shape[1])/2, 600 + i * 165 + (1 - k) * 90)
    # scene 4: tagline zoom (13.4-16.2s)
    if 13.4 <= t < 16.4:
        k = ease_out_back(min(1, max(0, (t - 13.5) / 0.9)))
        paste(frame, sp_tag1, (W - sp_tag1.shape[1])/2, 780 + (1 - k) * -200)
        paste(frame, sp_tag2, (W - sp_tag2.shape[1])/2, 940 + (1 - k) * 200)
    # scene 5: contact (16.0-18.0s)
    if t >= 16.0:
        k = ease_out_back(min(1, max(0, (t - 16.1) / 0.8)))
        pulse = 1 + 0.04 * math.sin(t * 6)
        paste(frame, sp_contact, (W - sp_contact.shape[1])/2, 820 + (1 - k) * 160)
        paste(frame, sp_phone, (W - sp_phone.shape[1])/2, 1000 + int((1 - pulse) * 10))
    writer.append_data(frame)

writer.close()
print("done:", N, "frames,", D, "s")
