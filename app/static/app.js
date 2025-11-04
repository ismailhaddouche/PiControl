document.addEventListener('DOMContentLoaded', function(){
  // Interceptar envíos AJAX de asignación de RFID si existen botones con data-assign
  document.querySelectorAll('[data-ajax-assign]').forEach(function(btn){
    btn.addEventListener('click', function(e){
      e.preventDefault();
      const empleadoId = this.dataset.empid;
      const input = document.querySelector('#rfid-input-' + empleadoId);
      if(!input) return alert('Campo RFID no encontrado');
      const rfid = input.value.trim();
      if(!rfid) return alert('Introduce un RFID');
      const url = '/admin/empleados/' + empleadoId + '/assign_ajax';
      fetch(url, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body: 'rfid_uid=' + encodeURIComponent(rfid)})
        .then(resp => resp.json())
        .then(data => {
          if(data && data.success){
            const flash = document.getElementById('flash');
            flash.textContent = 'RFID asignado a ' + data.nombre;
            flash.className = 'flash success';
            // actualizar celda rfid
            const cell = document.querySelector('#rfid-cell-' + empleadoId);
            if(cell) cell.textContent = data.rfid_uid || '';
            input.value = '';
          } else {
            alert(data?.error || 'Error al asignar RFID');
          }
        }).catch(err => {
          console.error(err);
          alert('Error de conexión al asignar RFID');
        });
    });
  });
});
