"""Soundtrack for brag.mp4: music and effects written as one piece.

120 bpm, A minor (Am - F - C - G, one chord per 2 s bar). Effects use notes from the same key and go
through the same reverb as the music, mixed underneath it.
"""

import wave

import numpy as np

SR = 48000
DUR = 22.0
N = int(SR * DUR)
rng = np.random.default_rng(7)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def tt(d):
    return np.arange(int(SR * d)) / SR


def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def onepole_lp(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):  # small signals only
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def lp_fast(x, cutoff, passes=2):
    # cheap low-pass via repeated moving average (fine for pads and noise)
    k = max(1, int(SR / cutoff / 2))
    ker = np.ones(k) / k
    for _ in range(passes):
        x = np.convolve(x, ker, mode="same")
    return x


def env_adsr(n, a, d, s, r, total):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    e[na : na + nd] = np.linspace(1, s, nd)
    nsus = int(total * SR)
    if nsus < n:
        e[nsus : nsus + nr] = np.linspace(e[nsus - 1] if nsus > 0 else s, 0, min(nr, n - nsus))
        e[nsus + nr :] = 0
    return e


# ---------------- harmony ----------------
# bar start times (2 s bars) and chords (MIDI notes)
AM, F, C, G = [57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]
ROOTS = {"Am": 45, "F": 41, "C": 48, "G": 43}
prog = ["Am", "F", "C", "G", "Am", "F", "C", "G", "Am", "F", "Am"]
CH = {"Am": AM, "F": F, "C": C, "G": G}

music = np.zeros(N)
fx = np.zeros(N)
kick_env = np.zeros(N)  # for side-chain ducking

# pad: detuned soft saws, low-passed, slow attack
for b, name in enumerate(prog):
    start = b * 2.0
    length = 2.6 if b < len(prog) - 1 else DUR - start
    x = tt(length)
    sig = np.zeros_like(x)
    for n in CH[name] + [CH[name][0] + 12]:
        for det in (-0.06, 0.06):
            f0 = midi(n + det)
            for h in range(1, 7):
                sig += np.sin(2 * np.pi * f0 * h * x + h) / (h * 1.6)
    sig = lp_fast(sig, 1400)
    e = env_adsr(len(x), 0.45, 0.6, 0.8, 0.6, length - 0.6)
    gain = 0.020 if start < 3.0 else 0.026
    add(music, start, sig * e, gain)

# pluck arpeggio: 8ths through the chord, an octave up
pattern = [0, 1, 2, 3, 2, 1, 0, 2]
for b, name in enumerate(prog[:-1]):
    notes = CH[name] + [CH[name][0] + 12]
    for k in range(8):
        t0 = b * 2.0 + k * 0.25
        n = notes[pattern[k] % len(notes)] + 12
        x = tt(0.6)
        f0 = midi(n)
        sig = (np.sin(2 * np.pi * f0 * x) + 0.35 * np.sin(4 * np.pi * f0 * x) + 0.12 * np.sin(6 * np.pi * f0 * x)) * np.exp(-x * 7.5)
        accent = 1.0 if k % 2 == 0 else 0.7
        gain = (0.045 if t0 < 3.0 else 0.055) * accent
        add(music, t0, sig, gain)

# bass from the reveal (3.0 s): root, 8th-note pulse
for b, name in enumerate(prog[:-1]):
    for k in range(8):
        t0 = b * 2.0 + k * 0.25
        if t0 < 3.0 or t0 >= 20.0:
            continue
        x = tt(0.24)
        f0 = midi(ROOTS[name])
        sig = np.tanh(1.6 * np.sin(2 * np.pi * f0 * x)) * np.exp(-x * 5) * np.minimum(1, x * 400)
        add(music, t0, sig, 0.075 if k % 2 == 0 else 0.05)

# kick on beats 1 and 3 (every 1.0 s) from 3.0 to 20.0
for i in range(3, 20):
    t0 = float(i)
    x = tt(0.35)
    f = 45 + 75 * np.exp(-x * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(ph) * np.exp(-x * 9)
    add(music, t0, sig, 0.19)
    add(kick_env, t0, np.exp(-tt(0.3) * 10), 1.0)

# off-beat hats from 6.5 s
for k in range(int((20.0 - 6.5) / 0.5)):
    t0 = 6.75 + k * 0.5
    x = tt(0.05)
    noise = rng.standard_normal(len(x))
    noise = noise - lp_fast(noise, 7000, 1)  # high-pass
    add(music, t0, noise * np.exp(-x * 90), 0.035)

# riser into the outro (17.0 -> 18.0) and a soft swell into the end card
x = tt(1.0)
noise = lp_fast(rng.standard_normal(len(x)), 3000)
add(music, 17.0, noise * (x**2), 0.05)
x = tt(0.8)
noise = lp_fast(rng.standard_normal(len(x)), 2000)
add(music, 19.0, noise * np.sin(np.pi * x / 0.8) ** 2, 0.04)

# final ringing chord (Am add9) on the end card
x = tt(DUR - 19.9)
sig = np.zeros_like(x)
for n in [57, 64, 67, 71, 72, 76]:
    f0 = midi(n)
    sig += (np.sin(2 * np.pi * f0 * x) + 0.25 * np.sin(4 * np.pi * f0 * x)) * np.exp(-x * 0.9)
add(music, 19.9, sig, 0.022)

# side-chain duck the pad/arp a little under the kick
music *= 1 - 0.28 * np.clip(kick_env, 0, 1)

# ---------------- effects (in key, under the music) ----------------


def tick(t0, note=81, gain=0.010):
    # tiny tuned key click (A5 / E6), very short
    x = tt(0.03)
    f0 = midi(note)
    sig = (np.sin(2 * np.pi * f0 * x) + 0.4 * rng.standard_normal(len(x)) * np.exp(-x * 400)) * np.exp(-x * 180)
    add(fx, t0, sig, gain)


def typing(a, b, rate, gain=0.008):
    t = a
    while t < b:
        tick(t, note=rng.choice([81, 88, 84]), gain=gain * rng.uniform(0.6, 1.0))
        t += rng.uniform(0.6, 1.4) / rate


typing(0.15, 2.3, 14, 0.006)     # ten engineers typing
typing(6.85, 7.3, 12)            # use-stack.sh
tick(7.95, 76); tick(8.25, 79); tick(8.55, 81, 0.014)   # selector steps (E5 G5 A5)  # noqa: E702
typing(8.6, 9.2, 12)
typing(11.95, 12.3, 10)          # make check
typing(15.5, 16.1, 14)


def pluck(t0, note, gain):
    x = tt(0.9)
    f0 = midi(note)
    sig = (np.sin(2 * np.pi * f0 * x) + 0.3 * np.sin(4 * np.pi * f0 * x)) * np.exp(-x * 6)
    add(fx, t0, sig, gain)


pluck(9.35, 76, 0.05); pluck(9.35, 81, 0.035)          # "Stack set to" confirm (E5 + A5)  # noqa: E702
pluck(11.75, 72, 0.03)                                  # Copilot suggestion accepted


def thud(t0, gain):
    # low, muted: A1 + A2 with a short body, minor third (C3) very quietly
    x = tt(0.5)
    sig = (np.sin(2 * np.pi * midi(33) * x) + 0.6 * np.sin(2 * np.pi * midi(45) * x) + 0.2 * np.sin(2 * np.pi * midi(48) * x)) * np.exp(-x * 9)
    sig = np.tanh(1.3 * sig)
    add(fx, t0, sig, gain)


thud(12.5, 0.16)                 # cross-domain-read
thud(16.2, 0.14)                 # contract-compat

for i, n in enumerate([69, 72, 76, 79, 81]):            # five green stacks: A4 C5 E5 G5 A5
    pluck(18.2 + i * 0.17, n + 12, 0.035)

# ---------------- shared space: simple stereo reverb ----------------


def reverb(x, mix, seconds=1.6):
    out = np.zeros((len(x), 2))
    for ch, delays in enumerate([(0.0297, 0.0371, 0.0411, 0.0437), (0.0311, 0.0353, 0.0429, 0.0451)]):
        acc = np.zeros(len(x))
        for d in delays:
            n = int(d * SR)
            g = 10 ** (-3 * d / seconds)
            y = np.zeros(len(x))
            # feedback comb via block processing
            for start in range(0, len(x), n):
                end = min(len(x), start + n)
                prev = y[start - n : end - n] if start >= n else np.zeros(end - start)
                y[start:end] = x[start:end] + g * prev
            acc += y
        out[:, ch] = lp_fast(acc / len(delays), 6000, 1)
    dry = np.stack([x, x], axis=1)
    return dry * (1 - mix) + out * mix


mix = reverb(music, 0.18) + reverb(fx, 0.30)

# gentle stereo width on the arp-heavy mid range, fade in/out, soft clip, normalise
fade = np.ones(N)
fade[: int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
fade[int(20.9 * SR) :] = np.linspace(1, 0, N - int(20.9 * SR))
mix *= fade[:, None]
mix = np.tanh(mix * 1.4) / 1.4
peak = np.max(np.abs(mix))
mix = mix / peak * 10 ** (-1.0 / 20)

pcm = (mix * 32767).astype(np.int16)
with wave.open("soundtrack.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote soundtrack.wav", DUR, "s")
