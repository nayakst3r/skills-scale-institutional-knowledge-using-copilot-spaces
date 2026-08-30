/* Guards the failure mode that killed the viewer once already.
   Classic <script> blocks share one global lexical scope: a top-level const in
   two blocks throws at parse time and the second block never runs, silently.
   Both scripts are executed here in one shared context, as a browser would. */
const fs = require('fs'), vm = require('vm');
const h = fs.readFileSync(process.argv[2], 'utf8');
const parts = [...h.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (parts.length < 2) { console.error('expected at least two script blocks'); process.exit(1); }

const top = b => { const s = new Set(); b.split('\n').forEach(l => {
  const m = /^(const|let|var|function)\s+([A-Za-z_$][\w$]*)/.exec(l); if (m) s.add(m[2]); }); return s; };
const clash = [...top(parts[1])].filter(x => top(parts[0]).has(x));
if (clash.length) { console.error('identifier collision across script blocks:', clash); process.exit(1); }

const store = {};
function el(t) { const e = { tagName: t, style: { setProperty() {} }, dataset: {}, children: [], _h: {},
  classList: { _s: new Set(), add(x){this._s.add(x)}, remove(x){this._s.delete(x)},
    toggle(x,v){ v ? this._s.add(x) : this._s.delete(x) }, contains(x){return this._s.has(x)} },
  attrs: {}, setAttribute(k,v){this.attrs[k]=v}, getAttribute(k){return this.attrs[k] ?? null},
  append(...c){this.children.push(...c)}, appendChild(c){this.children.push(c); return c},
  insertBefore(a){this.children.push(a)}, addEventListener(t,f){this._h[t]=f},
  querySelectorAll(){return []}, scrollTop: 0, innerHTML: '', textContent: '',
  get parentNode(){ return store.__s ?? (store.__s = el('div')); } }; return e; }
const doc = { createElement: el, createElementNS: (n,t) => el(t),
  getElementById: id => store[id] ?? (store[id] = el('div')),
  querySelectorAll: () => [], addEventListener() {}, body: el('body') };
const ctx = vm.createContext({ document: doc, console, Math, JSON, Object, Array, String,
  Number, Boolean, Set, Map, isNaN, parseInt, parseFloat, Date, RegExp, Error });
ctx.window = ctx;

try { parts.forEach((p, i) => vm.runInContext(p, ctx, { filename: 'script' + (i+1) })); }
catch (e) { console.error('uncaught exception:', e.message); process.exit(1); }

if (!/attributes/.test(store.modelBar?.innerHTML || '')) {
  console.error('model stat bar did not render'); process.exit(1); }

const wired = vm.runInContext(
  '(function(){var k=Object.keys(nodeEls);' +
  'for(var i=0;i<k.length;i++){var e=nodeEls[k[i]];' +
  'if(!e||!e._h||!e._h.click) return "no click handler on "+k[i];}' +
  'return true;})()', ctx);
if (wired !== true) { console.error('drill-down not wired:', wired); process.exit(1); }

for (const id of ['person', 'facility', 'nohc']) {
  vm.runInContext('nodeEls["' + id + '"]._h.click({stopPropagation:function(){}})', ctx);
  if (!store.apTitle.textContent) { console.error('panel empty for', id); process.exit(1); }
}
console.log('viewer OK — no collisions, no exceptions, drill-down wired, panel renders');
