"""Builds the first Inside the 23 content pack: 1080x1350 JPEG carousels."""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
W, H = 1080, 1350
BG = (14, 22, 18)
PITCH = (28, 98, 60)
PITCH_DARK = (22, 84, 50)
LINE = (240, 244, 240)
ACC = (247, 201, 40)      # us
OPP = (232, 72, 72)       # opposition
TXT = (245, 245, 240)
MUTED = (170, 185, 175)
F = "/usr/share/fonts/opentype/inter/"
def font(w, s): return ImageFont.truetype(F + {"b": "Inter-Bold.otf", "x": "Inter-ExtraBold.otf", "m": "Inter-Medium.otf", "r": "Inter-Regular.otf"}[w], s)

def wrap(d, text, fnt, width):
    out = []
    for para in text.split("\n"):
        words, line = para.split(), ""
        for w in words:
            t = (line + " " + w).strip()
            if d.textlength(t, font=fnt) <= width: line = t
            else: out.append(line); line = w
        out.append(line)
    return out

def text_block(d, x, y, text, fnt, fill, width, gap=1.25):
    for ln in wrap(d, text, fnt, width):
        d.text((x, y), ln, font=fnt, fill=fill); y += int(fnt.size * gap)
    return y

def frame(n, total, tag):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.text((70, 60), "INSIDE THE 23", font=font("x", 30), fill=ACC)
    d.text((W - 70, 60), tag, font=font("m", 26), fill=MUTED, anchor="ra")
    # progress dots
    for i in range(total):
        cx = W / 2 - (total - 1) * 14 + i * 28
        d.ellipse((cx - 6, H - 52, cx + 6, H - 40), fill=ACC if i == n else (60, 75, 66))
    return im, d

# ---------- pitch ----------
L, Wd = 91.4, 55.0
class Pitch:
    """Vertical view: their goal at the bottom, showing x_range metres up the pitch, full 55m width across."""
    def __init__(self, d, x0, y0, width, x_range=(0, 38)):
        self.d, self.x0, self.y0, self.xr = d, x0, y0, x_range
        self.s = width / Wd
        self.w, self.h = width, (x_range[1] - x_range[0]) * self.s
    def p(self, x, y): return (self.x0 + y * self.s, self.y0 + (self.xr[1] - x) * self.s)
    def draw(self):
        d, s = self.d, self.s
        x1, y1, x2, y2 = self.x0, self.y0, self.x0 + self.w, self.y0 + self.h
        n = 8
        for i in range(n):
            sy = y1 + i * self.h / n
            d.rectangle((x1, sy, x2, sy + self.h / n), fill=PITCH if i % 2 == 0 else PITCH_DARK)
        lw = max(3, int(s * 0.25))
        d.line([(x1, y1), (x1, y2), (x2, y2), (x2, y1)], fill=LINE, width=lw)
        for xm in (22.9, L / 2):
            if self.xr[0] <= xm <= self.xr[1]: d.line([self.p(xm, 0), self.p(xm, Wd)], fill=LINE, width=lw)
        self.circle(14.63, lw, False); self.circle(19.63, max(2, lw - 1), True)
        a = self.p(0, Wd / 2 - 1.83); b = self.p(-1.2, Wd / 2 + 1.83)
        d.rectangle((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), outline=LINE, width=lw)
        px, py = self.p(6.475, Wd / 2); d.ellipse((px - 4, py - 4, px + 4, py + 4), fill=LINE)
    def circle(self, r, lw, dashed):
        top, bot = Wd / 2 - 1.83, Wd / 2 + 1.83
        pts = [(r * math.cos(math.radians(90 - k)), top - r * math.sin(math.radians(90 - k))) for k in range(0, 91, 3)]
        pts += [(r * math.cos(math.radians(k)), bot + r * math.sin(math.radians(k))) for k in range(0, 91, 3)]
        pts = [self.p(*q) for q in pts]
        if dashed:
            for i in range(0, len(pts) - 1, 2): self.d.line([pts[i], pts[i + 1]], fill=LINE, width=lw)
        else: self.d.line(pts, fill=LINE, width=lw, joint="curve")
    def player(self, x, y, label, team):
        cx, cy = self.p(x, y); r = 22
        col = ACC if team == "us" else OPP
        self.d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=(20, 20, 20), width=3)
        self.d.text((cx, cy + 1), label, font=font("b", 20), fill=(20, 20, 20) if team == "us" else (255, 255, 255), anchor="mm")
    def ball(self, x, y):
        cx, cy = self.p(x, y); self.d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=(255, 255, 255), outline=(0, 0, 0), width=2)
    def arrow(self, a, b, col=LINE, dashed=False, width=5):
        (x1, y1), (x2, y2) = self.p(*a), self.p(*b)
        ang = math.atan2(y2 - y1, x2 - x1); hl = 22
        ex, ey = x2 - hl * 0.8 * math.cos(ang), y2 - hl * 0.8 * math.sin(ang)
        if dashed:
            dist = math.hypot(ex - x1, ey - y1); n = max(1, int(dist / 22))
            for i in range(0, n, 2):
                t1, t2 = i / n, min(1, (i + 1) / n)
                self.d.line([(x1 + (ex - x1) * t1, y1 + (ey - y1) * t1), (x1 + (ex - x1) * t2, y1 + (ey - y1) * t2)], fill=col, width=width)
        else: self.d.line([(x1, y1), (ex, ey)], fill=col, width=width)
        p1 = (x2 - hl * math.cos(ang - 0.45), y2 - hl * math.sin(ang - 0.45))
        p2 = (x2 - hl * math.cos(ang + 0.45), y2 - hl * math.sin(ang + 0.45))
        self.d.polygon([(x2, y2), p1, p2], fill=col)
    def zone(self, pts, col):
        ov = Image.new("RGBA", self.d._image.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.polygon([self.p(*q) for q in pts], fill=col)
        self.d._image.paste(Image.alpha_composite(self.d._image.convert("RGBA"), ov).convert("RGB"))

def legend(d, y):
    items = [(ACC, "Us"), (OPP, "Them")]
    x = 70
    for col, lab in items:
        d.ellipse((x, y, x + 26, y + 26), fill=col); d.text((x + 38, y - 2), lab, font=font("m", 26), fill=MUTED); x += 150
    d.line([(x, y + 13), (x + 50, y + 13)], fill=LINE, width=5); d.text((x + 62, y - 2), "Pass", font=font("m", 26), fill=MUTED); x += 170
    for i in range(0, 50, 16): d.line([(x + i, y + 13), (x + i + 9, y + 13)], fill=ACC, width=5)
    d.text((x + 62, y - 2), "Run", font=font("m", 26), fill=MUTED)

def save(im, folder, i):
    os.makedirs(folder, exist_ok=True); im.save(f"{folder}/{i:02d}.jpg", "JPEG", quality=92)

# =============== POST 1: Pro to club #1, the press ===============
def post1(folder):
    T, tag = 6, "PRO TO CLUB #1"
    # 1 cover
    im, d = frame(0, T, tag)
    y = text_block(d, 70, 170, "The press the pros run.", font("x", 92), TXT, 940, 1.1)
    y = text_block(d, 70, y + 10, "And the version your Saturday side can actually pull off.", font("m", 44), MUTED, 900)
    pt = Pitch(d, 70, 620, 940, (0, 30)); pt.draw()
    for (x, yy, l) in [(22, 18, "9"), (20, 37, "10"), (27, 27.5, "8")]: pt.player(x, yy, l, "us")
    for (x, yy, l) in [(10, 18, "5"), (10, 37, "6"), (24, 27.5, "4")]: pt.player(x, yy, l, "opp")
    pt.ball(12, 37.5)
    d.text((W - 70, 1205), "Swipe", font=font("b", 34), fill=ACC, anchor="ra")
    save(im, folder, 1)

    # 2 what the pros do
    im, d = frame(1, T, tag)
    d.text((70, 150), "WHAT THE PROS DO", font=font("b", 30), fill=ACC)
    text_block(d, 70, 200, "Front three screen the middle, not the ball.", font("x", 58), TXT, 940, 1.12)
    pt = Pitch(d, 70, 370, 940, (0, 38)); pt.draw()
    for (x, yy, l) in [(10, 18, "5"), (10, 37, "6"), (24, 27.5, "4"), (18, 5, "2"), (18, 50, "3")]: pt.player(x, yy, l, "opp")
    pt.ball(11.5, 37.5)
    pt.arrow((22, 30), (16, 33), ACC, dashed=True)
    pt.arrow((25, 22), (25, 25), ACC, dashed=True)
    for (x, yy, l) in [(22, 30, "9"), (25, 20, "10"), (28, 27.5, "8"), (36, 9, "7"), (36, 46, "11")]: pt.player(x, yy, l, "us")
    pt.arrow((36, 46), (27, 47), ACC, dashed=True)
    legend(d, 1040)
    text_block(d, 70, 1088, "The 9 curves his run so the only easy pass is up the line. The 8 sits on their 4. The 11 steps to their 3 the moment the ball goes wide.", font("r", 29), MUTED, 940)
    save(im, folder, 2)

    # 3 why it breaks at club level
    im, d = frame(2, T, tag)
    d.text((70, 150), "WHY IT BREAKS ON A SATURDAY", font=font("b", 30), fill=ACC)
    y = 330
    for h, b in [("Nobody runs that far, that often", "The pro version asks the front line to sprint to every pass. Your 9 has done that twice by the 15th minute."),
                 ("The gaps open behind", "One forward presses late and the whole thing has a hole in the middle. Their 4 turns and you're defending a 3 v 2."),
                 ("Nobody's calling it", "Pros press on a trigger they've all drilled. Club sides press when someone feels like it.")]:
        y = text_block(d, 70, y, h, font("x", 46), TXT, 940, 1.15)
        y = text_block(d, 70, y + 8, b, font("r", 34), MUTED, 940) + 50
    save(im, folder, 3)

    # 4 club version
    im, d = frame(3, T, tag)
    d.text((70, 150), "THE CLUB VERSION", font=font("b", 30), fill=ACC)
    text_block(d, 70, 200, "Give them the first pass. Trap the second.", font("x", 58), TXT, 940, 1.12)
    pt = Pitch(d, 70, 370, 940, (0, 38)); pt.draw()
    pt.zone([(18, 42), (34, 42), (34, 55), (18, 55)], (247, 201, 40, 70))
    for (x, yy, l) in [(10, 18, "5"), (10, 37, "6"), (24, 27.5, "4"), (25, 50, "3")]: pt.player(x, yy, l, "opp")
    pt.ball(26.5, 50.5)
    pt.arrow((11, 38), (24, 49.5), LINE)
    for (a, b) in [((31, 38), (29, 46)), ((26, 40), (23, 46.5)), ((36, 48), (31, 51))]: pt.arrow(a, b, ACC, dashed=True)
    for (x, yy, l) in [(31, 38, "9"), (26, 40, "8"), (36, 48, "11"), (22, 27, "10")]: pt.player(x, yy, l, "us")
    legend(d, 1040)
    text_block(d, 70, 1088, "Let their 6 play it wide. The sideline is your extra defender. Three of you close: one blocks inside, one comes from behind, one shuts the line. Your 10 sits on their 4 so there's no escape back.", font("r", 29), MUTED, 940)
    save(im, folder, 4)

    # 5 three calls
    im, d = frame(4, T, tag)
    d.text((70, 150), "THREE CALLS. THAT'S IT.", font=font("b", 30), fill=ACC)
    y = 320
    for call, b in [("\"Show wide\"", "Front line angles their runs so the middle is shut. Nobody dives in."),
                    ("\"Lock\"", "Ball's gone to the wide player. Nearest three go together, not one at a time."),
                    ("\"Back\"", "They've broken it. Everyone drops to the 23 and resets. No chasing.")]:
        d.text((70, y), call, font=font("x", 72), fill=TXT); y += 95
        y = text_block(d, 70, y, b, font("r", 36), MUTED, 940) + 60
    save(im, folder, 5)

    # 6 CTA
    im, d = frame(5, T, tag)
    y = text_block(d, 70, 300, "Try it Saturday.", font("x", 92), TXT, 940, 1.1)
    y = text_block(d, 70, y + 20, "Give it 15 minutes in the first half. Then tell us in the comments: did it trap anyone, or did your 9 give up after two goes?", font("m", 42), MUTED, 920)
    y = text_block(d, 70, y + 80, "Pro to club, every week.", font("b", 44), ACC, 940)
    text_block(d, 70, y + 10, "Follow @insidethe23hockey", font("b", 44), TXT, 940)
    save(im, folder, 6)

# =============== POST 2: meme carousel ===============
def post2(folder):
    pairs = [("\"I'll warm up in the first five minutes.\"", "My hamstring has 12 minutes left."),
             ("\"Let's play it out from the back.\"", "We're about to concede a short corner."),
             ("\"Umpire, that's a foot!\"", "I didn't see it. I'm just shouting."),
             ("\"Leave it, it's going out.\"", "It did not go out."),
             ("\"Just the one in the clubhouse.\"", "Sunday has been cancelled.")]
    T, tag = len(pairs) + 2, "CLUB HOCKEY, TRANSLATED"
    im, d = frame(0, T, tag)
    y = text_block(d, 70, 380, "Club hockey,", font("x", 110), TXT, 940, 1.05)
    y = text_block(d, 70, y, "translated.", font("x", 110), ACC, 940, 1.05)
    text_block(d, 70, y + 40, "What we say vs what it means.", font("m", 44), MUTED, 940)
    d.text((70, 1170), "Swipe", font=font("b", 34), fill=ACC)
    save(im, folder, 1)
    for i, (say, mean) in enumerate(pairs, start=1):
        im, d = frame(i, T, tag)
        d.text((70, 260), "WHAT WE SAY", font=font("b", 30), fill=MUTED)
        y = text_block(d, 70, 310, say, font("x", 66), TXT, 940, 1.15)
        y = max(y + 90, 700)
        d.line([(70, y - 45), (300, y - 45)], fill=ACC, width=6)
        d.text((70, y), "WHAT IT MEANS", font=font("b", 30), fill=ACC)
        text_block(d, 70, y + 50, mean, font("x", 66), ACC, 940, 1.15)
        save(im, folder, i + 1)
    im, d = frame(T - 1, T, tag)
    y = text_block(d, 70, 380, "Which one is your team?", font("x", 84), TXT, 940, 1.1)
    y = text_block(d, 70, y + 30, "Tag the teammate who says number 4 every single week.", font("m", 44), MUTED, 920)
    text_block(d, 70, y + 80, "Follow @insidethe23hockey", font("b", 44), ACC, 940)
    save(im, folder, T)

post1(os.path.join(OUT, "2026-11-25-pro-to-club-press"))
post2(os.path.join(OUT, "2026-11-30-club-hockey-translated"))
print("done")
