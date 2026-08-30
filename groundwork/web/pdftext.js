/* Minimal PDF text extractor — no dependencies.

   Written rather than pulled from a CDN for one reason: it can be tested
   against real funder PDFs in Node before shipping, whereas a library
   loaded inside the artifact sandbox can't be verified until it's live.

   Handles what funder application forms actually use: FlateDecode streams,
   page content text operators (Tj/TJ/'/"), and — critically — /ToUnicode
   CMaps, without which subset-embedded fonts extract as shifted gibberish
   (a real fillable form we tested came out with every character offset
   by 29). Scanned/image-only PDFs have no text layer at all; those are
   detected and reported rather than returned as noise.

   `inflate` is injected so Node (zlib) and the browser
   (DecompressionStream) can share the same code path. */

function latin1(bytes) {
  let s = "";
  for (let i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]);
  return s;
}

function findObjects(raw) {
  const objs = new Map();
  const re = /(\d+)\s+\d+\s+obj\b/g;
  let m;
  while ((m = re.exec(raw))) {
    const start = m.index + m[0].length;
    const end = raw.indexOf("endobj", start);
    if (end === -1) continue;
    objs.set(Number(m[1]), { body: raw.slice(start, end), start, end });
  }
  return objs;
}

function streamBytes(bytes, raw, obj) {
  const sIdx = raw.indexOf("stream", obj.start);
  if (sIdx === -1 || sIdx > obj.end) return null;
  let p = sIdx + 6;
  if (raw[p] === "\r") p++;
  if (raw[p] === "\n") p++;
  let e = raw.indexOf("endstream", p);
  if (e === -1) return null;
  let end = e;
  while (end > p && (raw[end - 1] === "\n" || raw[end - 1] === "\r")) end--;
  return bytes.subarray(p, end);
}

async function decodedStream(bytes, raw, obj, inflate) {
  const data = streamBytes(bytes, raw, obj);
  if (!data) return null;
  if (/\/Filter\s*(\/FlateDecode|\[\s*\/FlateDecode)/.test(obj.body)) {
    try { return latin1(await inflate(data)); } catch (e) { return null; }
  }
  if (/\/Filter/.test(obj.body)) return null; // DCT/CCITT image, or a filter we don't do
  return latin1(data);
}

/* ---- /ToUnicode CMap ---- */

function hexToChars(h) {
  let out = "";
  for (let i = 0; i + 3 < h.length + 1; i += 4) {
    const cp = parseInt(h.slice(i, i + 4), 16);
    if (!Number.isNaN(cp)) out += String.fromCharCode(cp);
  }
  return out;
}

function parseCMap(text) {
  const map = new Map();
  let widest = 1;
  for (const blk of text.match(/beginbfchar([\s\S]*?)endbfchar/g) || []) {
    for (const m of blk.matchAll(/<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>/g)) {
      map.set(parseInt(m[1], 16), hexToChars(m[2]));
      if (m[1].length > 2) widest = 2;
    }
  }
  for (const blk of text.match(/beginbfrange([\s\S]*?)endbfrange/g) || []) {
    for (const m of blk.matchAll(/<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(<([0-9A-Fa-f]+)>|\[([\s\S]*?)\])/g)) {
      const lo = parseInt(m[1], 16), hi = parseInt(m[2], 16);
      if (m[1].length > 2) widest = 2;
      if (m[4] !== undefined) {
        const base = m[4];
        for (let c = lo; c <= hi && c - lo < 65536; c++) {
          const shifted = (parseInt(base.slice(-4), 16) + (c - lo)).toString(16).padStart(4, "0");
          map.set(c, hexToChars(base.slice(0, -4) + shifted));
        }
      } else {
        const items = [...m[5].matchAll(/<([0-9A-Fa-f]+)>/g)];
        items.forEach((it, i) => map.set(lo + i, hexToChars(it[1])));
      }
    }
  }
  return { map, widest };
}

async function buildFontMaps(bytes, raw, objs, inflate) {
  const fonts = new Map(); // font object number -> {map, widest}
  for (const [num, obj] of objs) {
    if (!/\/Type\s*\/Font/.test(obj.body)) continue;
    const tu = obj.body.match(/\/ToUnicode\s+(\d+)\s+\d+\s+R/);
    if (!tu) { fonts.set(num, null); continue; }
    const cmapObj = objs.get(Number(tu[1]));
    if (!cmapObj) { fonts.set(num, null); continue; }
    const text = await decodedStream(bytes, raw, cmapObj, inflate);
    fonts.set(num, text ? parseCMap(text) : null);
  }
  return fonts;
}

/* ---- content stream text ---- */

function decodeString(str, font) {
  if (!font || !font.map.size) return str;
  let out = "";
  const step = font.widest === 2 ? 2 : 1;
  for (let i = 0; i < str.length; i += step) {
    const code = step === 2
      ? (str.charCodeAt(i) << 8) | (str.charCodeAt(i + 1) || 0)
      : str.charCodeAt(i);
    const mapped = font.map.get(code);
    out += mapped !== undefined ? mapped : (step === 1 ? str[i] : "");
  }
  return out;
}

function unescapePdfString(s) {
  return s.replace(/\\([nrtbf()\\]|[0-7]{1,3})/g, (m, g) => {
    if (g === "n" || g === "r") return " ";
    if (g === "t") return " ";
    if (g === "b" || g === "f") return "";
    if (g === "(" || g === ")" || g === "\\") return g;
    return String.fromCharCode(parseInt(g, 8));
  });
}

const TOKEN_RE = /\/([A-Za-z0-9#+._-]+)\s+([\d.]+)\s+Tf|\(((?:\\.|[^\\()])*)\)\s*(?:Tj|')|<([0-9A-Fa-f\s]+)>\s*(?:Tj|')|\[((?:[^\][]|\[[^\]]*\])*)\]\s*TJ|(T\*)|([-\d.]+)\s+([-\d.]+)\s+(?:Td|TD)|((?:[-\d.]+\s+){4})([-\d.]+)\s+([-\d.]+)\s+Tm|([-\d.]+)\s+TL/g;

function hexStr(h) {
  const hex = h.replace(/\s+/g, "");
  let s = "";
  for (let i = 0; i + 1 < hex.length; i += 2) s += String.fromCharCode(parseInt(hex.slice(i, i + 2), 16));
  return s;
}

/* Lines are decided by the text cursor's Y position alone — never by BT/ET.
   Real funder forms wrap EVERY fragment ("G", "rant ", "Requ") in its own
   BT...ET block at the same Y, so flushing on ET shattered the output into
   one word — sometimes one letter — per line. Same Y means same visual line;
   a meaningful Y change is a new one. A horizontal jump wider than the text
   could have advanced becomes a space, using a rough per-character width
   since we don't parse font metrics. */
function textFromContent(content, fontsByName) {
  const lines = [];
  let cur = "", font = null, size = 12;
  let x = 0, y = 0, lastY = null, penX = null, leading = 0;
  const flush = () => { const t = cur.replace(/\s+/g, " ").trim(); if (t) lines.push(t); cur = ""; };
  const advance = (text) => { if (penX !== null) penX += text.length * size * 0.6; };
  const moveTo = (nx, ny) => {
    if (lastY !== null && Math.abs(ny - lastY) > 2.5) flush();
    else if (cur && penX !== null && nx - penX > size * 0.45 && !cur.endsWith(" ")) cur += " ";
    x = nx; y = ny; lastY = ny; penX = nx;
  };
  const put = (text) => { cur += text; advance(text); };

  let m;
  TOKEN_RE.lastIndex = 0;
  while ((m = TOKEN_RE.exec(content))) {
    if (m[1] !== undefined) { font = fontsByName.get(m[1]) || null; size = Number(m[2]) || 12; continue; }
    if (m[3] !== undefined) { put(decodeString(unescapePdfString(m[3]), font)); continue; }
    if (m[4] !== undefined) { put(decodeString(hexStr(m[4]), font)); continue; }
    if (m[5] !== undefined) {
      for (const p of m[5].matchAll(/\(((?:\\.|[^\\()])*)\)|<([0-9A-Fa-f\s]+)>|(-?[\d.]+)/g)) {
        if (p[1] !== undefined) put(decodeString(unescapePdfString(p[1]), font));
        else if (p[2] !== undefined) put(decodeString(hexStr(p[2]), font));
        else if (Number(p[3]) < -180 && cur && !cur.endsWith(" ")) cur += " ";
      }
      continue;
    }
    if (m[6] !== undefined) { moveTo(x, y - (leading || size)); continue; }            // T*
    if (m[7] !== undefined) { moveTo(x + Number(m[7]), y + Number(m[8])); continue; }  // Td / TD
    if (m[10] !== undefined) { moveTo(Number(m[10]), Number(m[11])); continue; }       // Tm
    if (m[12] !== undefined) { leading = Math.abs(Number(m[12])) || size; continue; }  // TL
  }
  flush();
  return lines;
}

/* ---- page walk ---- */

function refsIn(s) { return [...s.matchAll(/(\d+)\s+\d+\s+R/g)].map(m => Number(m[1])); }

/* A dictionary value may be written inline (<< ... >>) or as an indirect
   reference to another object. Real forms use both — one fillable form we
   tested writes "/Font 1585 0 R", and handling only the inline form left its
   subset fonts unmapped, so two of its questions came out as shifted
   gibberish. Resolve either shape, following a chain of refs if needed. */
function dictFor(objs, body, key, depth = 0) {
  if (!body || depth > 4) return null;
  const inline = body.match(new RegExp("\\/" + key + "\\s*<<([\\s\\S]*?)>>"));
  if (inline) return inline[1];
  const ref = body.match(new RegExp("\\/" + key + "\\s+(\\d+)\\s+\\d+\\s+R"));
  if (ref) {
    const o = objs.get(Number(ref[1]));
    if (!o) return null;
    const nested = o.body.match(/<<([\s\S]*)>>/);
    return nested ? nested[1] : o.body;
  }
  return null;
}

function fontsForPage(objs, pageBody, fontMaps) {
  const byName = new Map();
  let fontDict = dictFor(objs, pageBody, "Font");
  if (!fontDict) {
    const resources = dictFor(objs, pageBody, "Resources");
    if (resources) fontDict = dictFor(objs, resources, "Font");
  }
  if (!fontDict) return byName;
  for (const fm of fontDict.matchAll(/\/([A-Za-z0-9#+._-]+)\s+(\d+)\s+\d+\s+R/g))
    byName.set(fm[1], fontMaps.get(Number(fm[2])) || null);
  return byName;
}

async function extractPdfText(buffer, inflate) {
  const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
  const raw = latin1(bytes);
  if (!raw.startsWith("%PDF")) throw new Error("That doesn't look like a PDF file.");
  const objs = findObjects(raw);
  const fontMaps = await buildFontMaps(bytes, raw, objs, inflate);

  const pages = [];
  for (const [, obj] of objs) {
    if (!/\/Type\s*\/Page[^s]/.test(obj.body)) continue;
    const fontsByName = fontsForPage(objs, obj.body, fontMaps);
    const cm = obj.body.match(/\/Contents\s*(\[[^\]]*\]|\d+\s+\d+\s+R)/);
    if (!cm) continue;
    let text = "";
    for (const ref of refsIn(cm[1])) {
      const co = objs.get(ref);
      if (!co) continue;
      const dec = await decodedStream(bytes, raw, co, inflate);
      if (dec) text += dec + "\n";
    }
    if (text) pages.push(textFromContent(text, fontsByName));
  }

  const lines = [];
  for (const p of pages) lines.push(...p);
  const out = lines.join("\n").replace(/[ \t]{2,}/g, " ").replace(/\n{3,}/g, "\n\n").trim();

  const letters = (out.match(/[A-Za-z]/g) || []).length;
  if (letters < 80) {
    throw new Error("This PDF has no readable text layer — it's most likely a scan or an image. Open it, select the text if you can, and paste it above instead.");
  }
  return out;
}

if (typeof module !== "undefined") module.exports = { extractPdfText, parseCMap, textFromContent };
