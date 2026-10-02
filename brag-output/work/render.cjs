// Renders brag.html frame by frame (each frame = render(t)), either as review stills or piped into ffmpeg.
//   node render.cjs stills 1.5 4.8 ...      -> stills/t=<sec>.png
//   node render.cjs video <seconds> <out>   -> silent video
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const FPS = 30;

(async () => {
  const [mode, ...args] = process.argv.slice(2);
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--font-render-hinting=none'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(__dirname, 'brag.html'));
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all(['Inter', 'JetBrains Mono'].map((f) => document.fonts.load(`600 40px "${f}"`)));
  });
  const loaded = await page.evaluate(() => [...document.fonts].filter((f) => f.status === 'loaded').map((f) => f.family));
  if (!loaded.includes('Inter') || !loaded.includes('JetBrains Mono')) throw new Error('fonts not loaded: ' + loaded);

  if (mode === 'stills') {
    fs.mkdirSync(path.join(__dirname, 'stills'), { recursive: true });
    for (const s of args) {
      await page.evaluate((t) => window.render(t), parseFloat(s));
      await page.screenshot({ path: path.join(__dirname, 'stills', `t=${s}.png`) });
    }
  } else {
    const seconds = parseFloat(args[0]);
    const out = args[1];
    const n = Math.round(seconds * FPS);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', String(FPS), out], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = 0; i < n; i++) {
      await page.evaluate((t) => window.render(t), i / FPS);
      const buf = await page.screenshot({ type: 'png' });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      if (i % 60 === 0) process.stdout.write(`frame ${i}/${n}\n`);
    }
    ff.stdin.end();
    await new Promise((r) => ff.on('close', r));
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
