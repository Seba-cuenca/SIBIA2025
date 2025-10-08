(function(){
  // Normaliza nombres para mapear entre stock y materiales_base
  function norm(s){
    return (s||'').toString().toLowerCase().trim()
      .normalize('NFD').replace(/[\u0300-\u036f]/g,'') // quita acentos
      .replace(/\s+/g,' ');
  }
  async function obtenerInfoMateriales(){
    try{
      const r = await fetch('/materiales_base');
      const j = await r.json();
      const tipos = {};
      const stMap = {};
      const alias = {};
      if (j && j.status === 'success' && Array.isArray(j.materiales)){
        j.materiales.forEach(m=>{
          if(m && m.nombre){
            const nombre = m.nombre;
            const nkey = norm(nombre);
            tipos[nombre] = (m.tipo||'').toLowerCase();
            tipos[nkey] = (m.tipo||'').toLowerCase();
            alias[nkey] = nombre; // referencia al nombre original
            // "st" suele venir como decimal 0..1; normalizar a 0..100
            const st = typeof m.st === 'number' ? m.st : (typeof m.st_porcentaje === 'number' ? m.st_porcentaje/100 : 0);
            const stVal = Math.max(0, Math.min(100, (st <= 1 ? st*100 : st)));
            stMap[nombre] = stVal;
            stMap[nkey] = stVal;
          }
        });
      }
      return {tipos, stMap, alias};
    }catch{return {};} 
  }

  async function cargarTablaStock(){
    const tbody = document.getElementById('stock-pro-rows');
    if(!tbody) return;
    try{
      ensureStockHeader();
      const [respStock, infoMat] = await Promise.all([
        fetch('/stock_actual'),
        obtenerInfoMateriales()
      ]);
      const data = await respStock.json();
      let mats = data && data.materiales ? data.materiales : {};
      if(Array.isArray(mats)){
        const obj = {}; mats.forEach(m=>{ if(m && m.nombre) obj[m.nombre]=m; }); mats = obj;
      }
      const filtro = (document.getElementById('filtro-stock')?.value||'').toLowerCase();
      const filas = Object.entries(mats).map(([nombre, info])=>{
        const nkey = norm(nombre);
        const tipo = (info.tipo || infoMat?.tipos?.[nkey] || infoMat?.tipos?.[nombre] || 'sin definir').toLowerCase();
        const st_pct = Number(info.st_porcentaje || info.st_pct || (infoMat?.stMap?.[nkey] ?? infoMat?.stMap?.[nombre] ?? 0));
        return {
          nombre,
          tipo,
          cantidad: Number(info.cantidad||info.total_tn||0),
          ts: info.timestamp || info.fecha || info.ultima_actualizacion || '',
          st_pct
        };
      }).filter(r=>!filtro || r.nombre.toLowerCase().includes(filtro))
        .sort((a,b)=> b.cantidad - a.cantidad);

      // Actualiza resumen porcentaje de sólidos
      actualizarResumenSolidos(filas);

      if(filas.length===0){
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Sin materiales</td></tr>';
      }else{
        tbody.innerHTML = filas.map(r=>`
          <tr data-material="${r.nombre}">
            <td>${r.nombre}</td>
            <td class="text-capitalize">${r.tipo}</td>
            <td class="text-end">${r.cantidad.toFixed(2)}</td>
            <td>
              <div class="d-flex justify-content-between align-items-center mb-1" style="font-size: 12px;">
                <span class="text-muted">${isFinite(r.st_pct)?r.st_pct.toFixed(0):0}%</span>
              </div>
              <div class="progress" style="height: 8px; background: #2c2f3b; border-radius: 6px; overflow: hidden;">
                <div class="progress-bar" style="width: ${Math.max(0,Math.min(100,(isFinite(r.st_pct)?r.st_pct:0)))}%; background: linear-gradient(90deg,#00c6ff,#0072ff);"></div>
              </div>
            </td>
            <td>${r.ts ? new Date(r.ts).toLocaleString('es-AR') : '-'}</td>
            <td class="text-center">
              <button class="btn btn-xs btn-outline-light" data-accion="ver">Ver</button>
            </td>
          </tr>`).join('');
      }
    }catch(e){
      tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Error cargando stock</td></tr>';
      console.warn('stock table load error', e);
    }
  }

  function actualizarResumenSolidos(filas){
    try{
      const porcEl = document.getElementById('stock-solidos-porc');
      const barEl = document.getElementById('stock-solidos-bar');
      if(!porcEl || !barEl) return;
      let total = 0;
      let totalSolidos = 0;
      for(const r of filas){
        const qty = isFinite(r.cantidad) ? r.cantidad : 0;
        total += qty;
        if((r.tipo||'').toLowerCase() === 'solido') totalSolidos += qty;
      }
      const pct = total > 0 ? Math.round((totalSolidos/total)*100) : 0;
      porcEl.textContent = `${pct}%`;
      barEl.style.width = `${pct}%`;
      // color adaptativo
      if(pct >= 70){
        barEl.style.background = 'linear-gradient(90deg,#2ecc71,#27ae60)';
      }else if(pct >= 40){
        barEl.style.background = 'linear-gradient(90deg,#f1c40f,#f39c12)';
      }else{
        barEl.style.background = 'linear-gradient(90deg,#e74c3c,#c0392b)';
      }
    }catch(err){ console.debug('No se pudo actualizar el resumen de sólidos', err); }
  }

  function bindControles(){
    const tbody = document.getElementById('stock-pro-rows');
    if(tbody && !tbody.dataset.clickbound){
      tbody.dataset.clickbound = '1';
      tbody.addEventListener('click', (ev)=>{
        const btn = ev.target.closest('button[data-accion="ver"]');
        if(!btn) return;
        const tr = btn.closest('tr');
        const nombre = tr?.dataset?.material || '-';
        const tipo = tr?.querySelector('td:nth-child(2)')?.textContent?.trim() || '';
        const cantidad = tr?.querySelector('td:nth-child(3)')?.textContent?.trim() || '';
        const stText = tr?.querySelector('td:nth-child(4) .text-muted')?.textContent?.trim() || '';
        mostrarPanelFlotante({nombre,tipo,cantidad,stText}, tr);
      });
    }

    const btnReset = document.getElementById('btn-reset-stock');
    if(btnReset && !btnReset.dataset.bound){
      btnReset.dataset.bound='1';
      btnReset.addEventListener('click', async ()=>{
        if(!confirm('¿Resetear todo el stock a 0?')) return;
        const r = await fetch('/stock/reset',{method:'POST'});
        const j = await r.json();
        if(j.status==='success') cargarTablaStock();
      });
    }
    const btnAuto = document.getElementById('btn-activar-descuento');
    if(btnAuto && !btnAuto.dataset.bound){
      btnAuto.dataset.bound='1';
      btnAuto.addEventListener('click', async ()=>{
        // Activar flag y aplicar una pasada inmediata
        await fetch('/stock_inteligente/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({activo:true})});
        const r = await fetch('/stock_inteligente/aplicar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ultima_hora:true})});
        try{ const j = await r.json(); }catch{}
        cargarTablaStock();
      });
    }
    const filtro = document.getElementById('filtro-stock');
    if(filtro && !filtro.dataset.bound){
      filtro.dataset.bound='1';
      filtro.addEventListener('input', ()=>cargarTablaStock());
    }

    // Ocultar panel flotante si existe
    const floating = document.querySelector('.stock-floating-panel');
    if(floating) floating.style.display='none';

    // Eliminar por completo la lista secundaria debajo de stock actual si aparece
    const killOldList = ()=>{
      document.querySelectorAll('#stock-list').forEach(el=> el.remove());
    };
    killOldList();
    // Evitar que se recree: observar el contenedor de stock
    const container = document.querySelector('#card-stock-actual, .stock-container, #tabla-stock-profesional')?.parentElement || document.body;
    try{
      const obs = new MutationObserver((mut)=>{
        mut.forEach(m=>{
          m.addedNodes && m.addedNodes.forEach(n=>{
            if(n.nodeType===1){
              if(n.id==='stock-list' || n.querySelector?.('#stock-list')){
                killOldList();
              }
            }
          });
        });
      });
      obs.observe(container, {childList:true, subtree:true});
    }catch(e){ /* noop */ }
  }

  function ensureStockHeader(){
    try{
      const table = document.getElementById('tabla-stock-profesional');
      if(!table) return;
      const thead = table.querySelector('thead');
      if(!thead) return;
      const tr = thead.querySelector('tr');
      if(!tr) return;
      const ths = Array.from(tr.children).map(el=>el.textContent.trim().toLowerCase());
      // if header doesn't already contain 'sólidos', rebuild
      if(!ths.some(t=>t.includes('sólidos'))){
        tr.innerHTML = `
          <th style="width:30%">Material</th>
          <th style="width:12%">Tipo</th>
          <th style="width:16%" class="text-end">Cantidad (tn)</th>
          <th style="width:18%">Sólidos (%)</th>
          <th style="width:16%">Última actualización</th>
          <th style="width:8%" class="text-center">Acciones</th>`;
      }
    }catch(err){ /* noop */ }
  }

  function mostrarPanelFlotante(info, anchor){
    let panel = document.querySelector('#stock-material-panel');
    if(!panel){
      panel = document.createElement('div');
      panel.id = 'stock-material-panel';
      panel.style.position = 'fixed';
      panel.style.right = '20px';
      panel.style.bottom = '20px';
      panel.style.background = 'rgba(30,35,45,0.98)';
      panel.style.border = '1px solid #3a3f51';
      panel.style.borderRadius = '8px';
      panel.style.padding = '12px 14px';
      panel.style.color = '#fff';
      panel.style.zIndex = '9999';
      panel.style.minWidth = '260px';
      panel.innerHTML = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;"><strong>Detalle material</strong><button id="close-stock-panel" class="btn btn-sm btn-outline-light">×</button></div><div id="stock-panel-body"></div>';
      document.body.appendChild(panel);
      panel.querySelector('#close-stock-panel').addEventListener('click',()=>{ panel.style.display='none'; });
    }
    const body = panel.querySelector('#stock-panel-body');
    body.innerHTML = `
      <div><span class="text-muted">Material:</span> <strong>${info.nombre}</strong></div>
      <div><span class="text-muted">Tipo:</span> ${info.tipo}</div>
      <div><span class="text-muted">Cantidad:</span> ${info.cantidad}</div>
      <div><span class="text-muted">Sólidos:</span> ${info.stText||'-'}</div>
    `;
    panel.style.display = 'block';
  }

  document.addEventListener('DOMContentLoaded', ()=>{
    bindControles();
    ensureStockHeader();
    cargarTablaStock();
    // refresh periódico
    setInterval(cargarTablaStock, 5000);
  });
})();
