/* ════════════════════════════════════════════════
   RakiCrops AI – app.js
   Handles: district load, prediction, AI plan modal
════════════════════════════════════════════════ */

const API = ''; // empty = same origin

/* ── Markdown → HTML (simple) ──────────────────────────────────────────── */
function simpleMarkdown(md) {
  return md
    // Headers
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Inline code
    .replace(/`(.+?)`/g, '<code>$1</code>')
    // HR
    .replace(/^---+$/gm, '<hr />')
    // Bullet lists (greedy consecutive lines)
    .replace(/(^- .+$\n?)+/gm, (block) => {
      const items = block.trim().split('\n').map(l => `<li>${l.slice(2)}</li>`).join('');
      return `<ul>${items}</ul>`;
    })
    // Paragraphs (double newline)
    .replace(/\n{2,}/g, '</p><p>')
    // Wrap
    .replace(/^/, '<p>').replace(/$/, '</p>')
    // Clean up empty <p></p>
    .replace(/<p>\s*<\/p>/g, '');
}

/* ── Load Districts ─────────────────────────────────────────────────────── */
async function loadDistricts() {
  try {
    const res = await fetch(`${API}/api/districts`);
    const districts = await res.json();
    const sel = document.getElementById('district');
    sel.innerHTML = '<option value="">— Select district —</option>';
    districts.forEach(d => {
      const opt = document.createElement('option');
      opt.value = d; opt.textContent = d;
      sel.appendChild(opt);
    });
    // default
    sel.value = 'Krishna';
  } catch (e) {
    console.error('Could not load districts', e);
  }
}

/* ── Prediction ─────────────────────────────────────────────────────────── */
const formEl      = document.getElementById('predictForm');
const predictBtn  = document.getElementById('predictBtn');
const spinner     = document.getElementById('predictSpinner');
const btnText     = predictBtn.querySelector('.btn-text');
const placeholder = document.getElementById('resultsPlaceholder');
const resultsCont = document.getElementById('resultsContent');
const cropListEl  = document.getElementById('cropList');

let lastInputs = {};

formEl.addEventListener('submit', async (e) => {
  e.preventDefault();

  // loading state
  btnText.textContent = 'Predicting…';
  spinner.classList.remove('hidden');
  predictBtn.disabled = true;

  const fd = new FormData(formEl);
  const rawPayload = {};
  for (const [k, v] of fd.entries()) rawPayload[k] = v;

  // Cast numeric fields (FormData always returns strings)
  const INT_FIELDS   = ['year', 'soil_texture'];
  const FLOAT_FIELDS = ['NDVI_mean', 'elevation', 'evapotranspiration', 'rain',
                        'slope', 'soil_carbon', 'soil_ph', 'temp'];
  const payload = { ...rawPayload };
  INT_FIELDS.forEach(f => { if (payload[f] !== undefined) payload[f] = parseInt(payload[f], 10); });
  FLOAT_FIELDS.forEach(f => { if (payload[f] !== undefined) payload[f] = parseFloat(payload[f]); });

  lastInputs = { ...rawPayload }; // keep as strings for display in AI prompt

  try {
    const res  = await fetch(`${API}/api/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.error) { alert('Error: ' + data.error); return; }

    renderCrops(data.top5);
    placeholder.classList.add('hidden');
    resultsCont.classList.remove('hidden');

    // smooth scroll to results
    resultsCont.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  } catch (err) {
    alert('Request failed: ' + err.message);
  } finally {
    btnText.textContent = '🔍 Predict Crops';
    spinner.classList.add('hidden');
    predictBtn.disabled = false;
  }
});

function renderCrops(crops) {
  const emojis  = ['🥇','🥈','🥉','4️⃣','5️⃣'];
  const maxProb = crops[0].probability;

  cropListEl.innerHTML = crops.map((c, i) => `
    <div class="crop-item" data-crop="${c.crop}" role="button" tabindex="0">
      <div class="crop-rank rank-${i+1}">${i+1}</div>
      <div class="crop-info">
        <div class="crop-name">${emojis[i]} ${c.crop}</div>
        <div class="crop-prob">Confidence: ${c.probability}%</div>
        <div class="crop-prob-bar">
          <div class="crop-prob-fill" style="width:${(c.probability / maxProb * 100).toFixed(1)}%"></div>
        </div>
      </div>
      <div class="crop-cta">Get Plan →</div>
    </div>
  `).join('');

  // Click handlers
  cropListEl.querySelectorAll('.crop-item').forEach(el => {
    el.addEventListener('click', () => openPlan(el.dataset.crop));
    el.addEventListener('keydown', (e) => { if (e.key === 'Enter') openPlan(el.dataset.crop); });
  });
}

/* ── AI Plan Modal ──────────────────────────────────────────────────────── */
const modal       = document.getElementById('planModal');
const modalClose  = document.getElementById('modalClose');
const backdrop    = document.getElementById('modalBackdrop');
const modalTitle  = document.getElementById('modalTitle');
const modalBadge  = document.getElementById('modalCropBadge');
const planLoading = document.getElementById('planLoading');
const planContent = document.getElementById('planContent');

const CROP_EMOJI = {
  'Rice':              '🌾', 'Wheat':        '🌾', 'Maize':     '🌽',
  'Cotton':            '🌿', 'Groundnut':    '🥜', 'Sugarcane': '🍬',
  'Ragi':              '🌾', 'Jowar':        '🌾', 'Bajra':     '🌾',
  'Arhar/Tur':         '🫘', 'Gram':         '🫘', 'Urad':      '🫘',
  'Soyabean':          '🫘', 'Sunflower':    '🌻', 'Tapioca':   '🥔',
  'Sweet potato':      '🍠', 'Onion':        '🧅', 'Potato':    '🥔',
  'Tobacco':           '🍃', 'Sesamum':      '🌿', 'Safflower': '🌼',
  'Rapeseed mustard':  '🌻', 'Niger seed':   '🌿', 'Castor seed':'🌿',
  'Horse gram':        '🫘', 'Cowpea':       '🫘', 'Green Gram':'🫘',
  'Dry chillies':      '🌶️', 'Coriander':   '🌿', 'Guar':      '🌿',
  'Small millets':     '🌾',
};

function openPlan(crop) {
  const emoji = CROP_EMOJI[crop] || '🌾';
  modalBadge.textContent  = `${emoji} ${crop}`;
  modalTitle.textContent  = `Agriculture Plan`;
  planContent.classList.add('hidden');
  planContent.innerHTML   = '';
  planLoading.classList.remove('hidden');
  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';

  // fetch plan
  fetch(`${API}/api/farming-plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ crop, inputs: lastInputs })
  })
  .then(async r => {
    const data = await r.json();
    planLoading.classList.add('hidden');
    if (!r.ok) {
      // FastAPI error shape: { detail: "..." }
      const msg = data.detail || JSON.stringify(data);
      planContent.innerHTML = `<p style="color:#f87171;font-weight:600">⚠️ ${msg}</p>`;
    } else {
      planContent.innerHTML = simpleMarkdown(data.plan);
    }
    planContent.classList.remove('hidden');
  })
  .catch(err => {
    planLoading.classList.add('hidden');
    planContent.innerHTML = `<p style="color:#f87171">Request failed: ${err.message}</p>`;
    planContent.classList.remove('hidden');
  });
}

function closeModal() {
  modal.classList.add('hidden');
  document.body.style.overflow = '';
}

modalClose.addEventListener('click', closeModal);
backdrop.addEventListener('click', closeModal);
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });

/* ── Init ───────────────────────────────────────────────────────────────── */
loadDistricts();
