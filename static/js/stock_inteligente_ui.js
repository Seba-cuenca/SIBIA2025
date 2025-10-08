(function(){
  try{
    // Styles
    const css = `
      .stock-floating-panel{position:fixed;right:18px;bottom:18px;z-index:10000;background:rgba(18,22,30,.9);border:1px solid #2a3342;border-radius:10px;padding:12px 14px;box-shadow:0 8px 24px rgba(0,0,0,.35);color:#dbe2ef;backdrop-filter:blur(6px)}
      .stock-floating-panel h5{margin:0 0 8px 0;font-weight:600;color:#8fd1ff}
      .stock-floating-panel .btn{cursor:pointer;border:1px solid #2a3342;border-radius:8px;padding:8px 10px;margin:4px 0;display:block;background:#1e2532;color:#e6edf7}
      .stock-floating-panel .btn.primary{background:#1363DF;border-color:#0d4db3}
      .stock-floating-panel .btn.warn{background:#7a1f1f;border-color:#8a2a2a}
      .stock-floating-panel .row{display:flex;gap:6px;align-items:center}
      .stock-floating-panel label{display:flex;gap:8px;align-items:center;font-size:13px}
      .modal-backdrop-sibia{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:9998;display:none}
      .modal-sibia{position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);background:#0f1624;color:#e6edf7;width:min(1100px,92vw);max-height:80vh;border-radius:12px;border:1px solid #22314a;overflow:hidden;z-index:9999;display:none}
      .modal-sibia header{padding:14px 16px;border-bottom:1px solid #22314a;display:flex;justify-content:space-between;align-items:center;background:#111a2b}
      .modal-sibia header h4{margin:0;font-weight:700;color:#8fd1ff}
      .modal-sibia header .close{cursor:pointer;font-size:22px;color:#9fb2cc}
      .modal-sibia .content{padding:12px 14px;overflow:auto;max-height:calc(80vh - 56px)}
      .table-pro{width:100%;border-collapse:separate;border-spacing:0}
      .table-pro thead th{position:sticky;top:0;background:#111a2b;color:#bcd3ee;text-align:left;padding:10px;border-bottom:1px solid #22314a;font-weight:600}
      .table-pro tbody tr{border-bottom:1px solid #1e2a3f}
      .table-pro tbody tr:hover{background:#122036}
      .table-pro td{padding:10px}
      .badge{display:inline-block;padding:3px 8px;border-radius:999px;font-size:12px}
      .badge.solido{background:#1f3b57;color:#8fd1ff}
      .badge.liquido{background:#264a2b;color:#79e29b}
      .bar{height:8px;background:#1a2436;border-radius:6px;overflow:hidden}
      .bar>span{display:block;height:100%;background:linear-gradient(90deg,#3ba4ff,#14b8a6)}
      .muted{color:#9fb2cc;font-size:12px}
      .actions{display:flex;gap:8px}
    `;
    const style = document.createElement('style'); style.textContent = css; document.head.appendChild(style);

    // Floating panel
    const panel = document.createElement('div');
    panel.className = 'stock-floating-panel';
    panel.innerHTML = `
      <h5>Stock inteligente</h5>
      <div class="row" style="justify-content:space-between;margin-bottom:8px;">
        <label><input type="checkbox" id="toggleStockInteligente"> Activar descuento automático</label>
      </div>
      <div class="actions">
        <button class="btn primary" id="btnAplicarAhora">Aplicar ahora</button>
        <button class="btn" id="btnVerStock">Ver stock</button>
        <button class="btn warn" id="btnResetStock">Reset 0</button>
      </div>
      <div class="muted" id="stockPanelMsg" style="margin-top:6px;display:none;"></div>
    `;
    document.body.appendChild(panel);

    // Modal + backdrop
    const backdrop = document.createElement('div'); backdrop.id='stockModalBackdrop'; backdrop.className='modal-backdrop-sibia';
    const modal = document.createElement('div'); modal.id='stockModal'; modal.className='modal-sibia'; modal.setAttribute('role','dialog'); modal.setAttribute('aria-modal','true');
    modal.innerHTML = `
      <header>
        <h4 id="stockModalTitle">Stock actual - Vista profesional</h4>
        <span id="closeStockModal" class="close">×</span>
      </header>
      <div class="content">
        <table class="table-pro" id="stockProTable">
          <thead>
            <tr>
              <th>Material</th>
              <th>Tipo</th>
              <th>Stock (TN)</th>
              <th>ST%</th>
              <th>KW/TN</th>
              <th>Últ. act.</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>`;
    document.body.appendChild(backdrop); document.body.appendChild(modal);

    const el = (q)=>document.querySelector(q);
    const msg = (t,ok=true)=>{ const m=el('#stockPanelMsg'); if(!m) return; m.style.display='block'; m.style.color= ok?'#8fd1ff':'#ff9aa2'; m.textContent=t; setTimeout(()=>{m.style.display='none'}, 4000); };

    const openModal=()=>{ modal.style.display='block'; backdrop.style.display='block'; };
    const closeModal=()=>{ modal.style.display='none'; backdrop.style.display='none'; };
    modal.querySelector('#closeStockModal').addEventListener('click', closeModal);
    backdrop.addEventListener('click', closeModal);

    async function renderStockPro(){
      try{
        const r = await fetch('/stock_actual');
        const data = await r.json();
        const tbody = el('#stockProTable tbody');
        if(!tbody) return; tbody.innerHTML='';
        const materiales = (data && data.materiales) ? data.materiales : [];
        materiales.sort((a,b)=> (b.total_tn||0) - (a.total_tn||0));
        for(const m of materiales){
          const tipo = (m.tipo||'solido').toLowerCase();
          const st = Number(m.st_porcentaje||0).toFixed(1);
          const kw = Number(m['kw/tn']||m.kw_tn||0).toFixed(2);
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${m.nombre||m.material}</td>
            <td><span class="badge ${tipo}">${tipo==='liquido'?'Líquido':'Sólido'}</span></td>
            <td>${Number(m.total_tn||0).toLocaleString('es-AR',{maximumFractionDigits:2})}</td>
            <td>
              <div class="bar"><span style="width:${Math.min(100, Math.max(0, st))}%"></span></div>
              <div class="muted">${st}%</div>
            </td>
            <td>${kw}</td>
            <td class="muted">${m.ultima_actualizacion||'-'}</td>`;
          tbody.appendChild(tr);
        }
      }catch(e){ console.warn('Error renderStockPro', e); }
    }

    // Toggle activar/desactivar
    el('#toggleStockInteligente').addEventListener('change', async (ev)=>{
      try{
        const activo = ev.target.checked;
        const r = await fetch('/stock_inteligente/config', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({activo})});
        const j = await r.json();
        if(j.status==='success'){ msg(activo?'Activado':'Desactivado'); }
        else { msg('Error configurando', false); }
      }catch(e){ msg('Error de red', false); }
    });

    // Aplicar ahora
    el('#btnAplicarAhora').addEventListener('click', async ()=>{
      try{
        const r = await fetch('/stock_inteligente/aplicar', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ultima_hora:true})});
        const j = await r.json();
        if(j.status==='success'){ msg(`Aplicado. Cambios: ${j.total_aplicadas}`); renderStockPro(); }
        else { msg('Error aplicando', false); }
      }catch(e){ msg('Error de red', false); }
    });

    // Ver stock (modal)
    el('#btnVerStock').addEventListener('click', ()=>{ renderStockPro(); openModal(); });

    // Reset stock
    el('#btnResetStock').addEventListener('click', async ()=>{
      if(!confirm('¿Seguro que quieres resetear todo el stock a 0?')) return;
      try{
        const r = await fetch('/stock/reset', {method:'POST'});
        const j = await r.json();
        if(j.status==='success'){ msg('Stock reseteado'); renderStockPro(); }
        else { msg('Error reseteando', false); }
      }catch(e){ msg('Error de red', false); }
    });
  }catch(err){ console.warn('stock_inteligente_ui init error', err); }
})();
