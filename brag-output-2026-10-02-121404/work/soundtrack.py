"""Soundtrack for brag.mp4 (v2): music and effects as one piece, timed from timeline.js.

120 bpm, A minor (Am - F - C - G, one chord per 2 s bar). Effects use notes from the key and share
the music's reverb, mixed underneath it.
"""

import json
import re
import wave

import numpy as np

TL = json.loads(re.search(r"window\.TL\s*=\s*(\{.*\});", open("timeline.js").read(), re.S).group(1))
SR = 48000
DUR = TL["dur"]
N = int(SR * DUR)
rng = np.random.default_rng(7)
SC = TL["scenes"]


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def tt(d):
    return np.arange(int(SR * d)) / SR


def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i >= len(buf) or i < 0:
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def lp(x, cutoff, passes=2):
    k = max(1, int(SR / cutoff / 2))
    ker = np.ones(k) / k
    for _ in range(passes):
        x = np.convolve(x, ker, mode="same")
    return x


def in_any(t, ranges):
    return any(a <= t < b for a, b in ranges)


AM, F, C, G = [57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]
CH = {"Am": AM, "F": F, "C": C, "G": G}
ROOTS = {"Am": 45, "F": 41, "C": 48, "G": 43}
nbars = int(np.ceil(DUR / 2.0))
prog = [["Am", "F", "C", "G"][b % 4] for b in range(nbars)]
prog[-1] = prog[-2] = prog[-3] = "Am"  # resolve on the close

music = np.zeros(N)
fx = np.zeros(N)
kick_env = np.zeros(N)

# sections
problem, title, close = SC["problem"], SC["title"], SC["close"]
learn = SC["learn"]
groove = [(title[0], learn[0]), (close[0], close[0] + 3.0)]
question = (6.0, problem[1])

# ---------- pad ----------
for b, name in enumerate(prog):
    start = b * 2.0
    length = min(2.6, DUR - start)
    x = tt(length)
    sig = np.zeros_like(x)
    for n in CH[name] + [CH[name][0] + 12]:
        for det in (-0.06, 0.06):
            f0 = midi(n + det)
            for h in range(1, 7):
                sig += np.sin(2 * np.pi * f0 * h * x + h) / (h * 1.6)
    sig = lp(sig, 1300)
    e = np.minimum(1, x / 0.45) * np.minimum(1, np.maximum(0, (length - x) / 0.6))
    gain = 0.018 if start < title[0] else 0.024
    if in_any(start, [learn]):
        gain = 0.03
    add(music, start, sig * e, gain)

# ---------- pluck arpeggio ----------
pattern = [0, 1, 2, 3, 2, 1, 0, 2]
for b, name in enumerate(prog):
    notes = CH[name] + [CH[name][0] + 12]
    for k in range(8):
        t0 = b * 2.0 + k * 0.25
        if t0 >= close[0] + 3.0:
            continue
        sparse = in_any(t0, [question, learn]) and k % 2 == 1
        if sparse:
            continue
        x = tt(0.6)
        f0 = midi(notes[pattern[k] % len(notes)] + 12)
        sig = (np.sin(2 * np.pi * f0 * x) + 0.35 * np.sin(4 * np.pi * f0 * x) + 0.12 * np.sin(6 * np.pi * f0 * x)) * np.exp(-x * 7.5)
        gain = (0.038 if t0 < title[0] else 0.05) * (1.0 if k % 2 == 0 else 0.7)
        add(music, t0, sig, gain)

# ---------- bass: soft pulse in the problem, full in the groove ----------
for b, name in enumerate(prog):
    for k in range(8):
        t0 = b * 2.0 + k * 0.25
        full = in_any(t0, groove)
        pulse = problem[0] + 1.0 <= t0 < question[0]
        if not (full or pulse):
            continue
        x = tt(0.24)
        sig = np.tanh(1.6 * np.sin(2 * np.pi * midi(ROOTS[name]) * x)) * np.exp(-x * 5) * np.minimum(1, x * 400)
        add(music, t0, sig, (0.07 if k % 2 == 0 else 0.045) if full else 0.035)

# ---------- kick (beats 1 and 3) in the groove ----------
for i in range(int(DUR)):
    t0 = float(i)
    if not in_any(t0, groove):
        continue
    x = tt(0.35)
    f = 45 + 75 * np.exp(-x * 30)
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 9)
    add(music, t0, sig, 0.19)
    add(kick_env, t0, np.exp(-tt(0.3) * 10), 1.0)

# ---------- off-beat hats ----------
for k in range(int(DUR / 0.5)):
    t0 = 0.25 + k * 0.5
    if not (in_any(t0, groove) or 3.5 <= t0 < question[0]):
        continue
    x = tt(0.05)
    noise = rng.standard_normal(len(x))
    noise = noise - lp(noise, 7000, 1)
    add(music, t0, noise * np.exp(-x * 90), 0.03)

# ---------- risers / whooshes into scene changes ----------
for t0 in TL["events"]["whoosh"]:
    x = tt(0.5)
    noise = lp(rng.standard_normal(len(x)), 2500)
    add(music, t0 - 0.3, noise * (x / 0.5) ** 2, 0.03)
x = tt(2.0)
add(music, question[1] - 2.0, lp(rng.standard_normal(len(x)), 3000) * (x / 2.0) ** 2, 0.05)  # build into the title

# ---------- impacts (title, step 1, close) ----------
for t0 in TL["events"]["impact"]:
    x = tt(1.6)
    sig = np.zeros_like(x)
    for n in [45, 57, 64]:
        sig += np.sin(2 * np.pi * midi(n) * x) * np.exp(-x * 2.2)
    sig += lp(rng.standard_normal(len(x)), 900) * np.exp(-x * 6) * 0.4
    add(music, t0, sig, 0.05)

# ---------- final chord on the brand ----------
x = tt(DUR - (close[0] + 3.0))
sig = np.zeros_like(x)
for n in [57, 64, 67, 71, 72, 76]:
    sig += (np.sin(2 * np.pi * midi(n) * x) + 0.25 * np.sin(4 * np.pi * midi(n) * x)) * np.exp(-x * 0.45)
add(music, close[0] + 3.0, sig, 0.022)

music *= 1 - 0.28 * np.clip(kick_env, 0, 1)

# ---------- effects ----------


def tick(t0, note=81, gain=0.008):
    x = tt(0.03)
    sig = (np.sin(2 * np.pi * midi(note) * x) + 0.4 * rng.standard_normal(len(x)) * np.exp(-x * 400)) * np.exp(-x * 180)
    add(fx, t0, sig, gain)


def pluck(t0, note, gain, decay=6):
    x = tt(1.0)
    f0 = midi(note)
    add(fx, t0, (np.sin(2 * np.pi * f0 * x) + 0.3 * np.sin(4 * np.pi * f0 * x)) * np.exp(-x * decay), gain)


def thud(t0, gain=0.14):
    x = tt(0.5)
    sig = (np.sin(2 * np.pi * midi(33) * x) + 0.6 * np.sin(2 * np.pi * midi(45) * x) + 0.2 * np.sin(2 * np.pi * midi(48) * x)) * np.exp(-x * 9)
    add(fx, t0, np.tanh(1.3 * sig), gain)


def chord(t0, notes, gain):
    for n in notes:
        pluck(t0, n, gain, decay=3.5)


for a, b in TL["events"]["typing"]:
    t = a
    while t < b:
        tick(t, note=int(rng.choice([81, 84, 88])), gain=0.008 * rng.uniform(0.6, 1.0))
        t += rng.uniform(0.06, 0.11)

for t0 in TL["events"]["fail"]:
    thud(t0, 0.12 if t0 < problem[1] else 0.15)
for t0 in TL["events"]["pass"]:
    pluck(t0, 76, 0.04); pluck(t0 + 0.12, 81, 0.035)  # noqa: E702

# PR checks: a soft tick per pill result, a warm chord on each merge
lanes = TL["lanes"]
for k, ln in lanes.items():
    runs = [ln["checks"]] + ([ln["recheck"]] if "recheck" in ln else [])
    for r0 in runs:
        for i in range(5):
            tick(r0 + TL["checkLead"] + TL["checkStep"] * i, note=[69, 72, 76, 79, 81][i], gain=0.012)
    chord(ln["merge"], [69, 76, 81], 0.022)

# pipeline stages light up: ascending A-minor notes; production lands on the octave
for i, t0 in enumerate(TL["promoteStages"]):
    pluck(t0, [69, 72, 76, 79, 81, 93][i], 0.035 if i < 5 else 0.045)

# the practice learns: four soft notes as the steps connect
for i, t0 in enumerate([66.7, 67.5, 68.3, 69.3]):
    pluck(t0, [72, 76, 79, 84][i], 0.03, decay=4)

# ---------- shared space: simple stereo reverb ----------


def reverb(x, mix, seconds=1.6):
    out = np.zeros((len(x), 2))
    for ch, delays in enumerate([(0.0297, 0.0371, 0.0411, 0.0437), (0.0311, 0.0353, 0.0429, 0.0451)]):
        acc = np.zeros(len(x))
        for d in delays:
            n = int(d * SR)
            g = 10 ** (-3 * d / seconds)
            y = np.zeros(len(x))
            for start in range(0, len(x), n):
                end = min(len(x), start + n)
                prev = y[start - n : end - n] if start >= n else np.zeros(end - start)
                y[start:end] = x[start:end] + g * prev
            acc += y
        out[:, ch] = lp(acc / len(delays), 6000, 1)
    return np.stack([x, x], axis=1) * (1 - mix) + out * mix


mix = reverb(music, 0.18) + reverb(fx, 0.30)
fade = np.ones(N)
fade[: int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
fo = int((DUR - 1.2) * SR)
fade[fo:] = np.linspace(1, 0, N - fo)
mix *= fade[:, None]
mix = np.tanh(mix * 1.4) / 1.4
mix = mix / np.max(np.abs(mix)) * 10 ** (-1.0 / 20)

with wave.open("soundtrack.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("wrote soundtrack.wav", DUR, "s")
