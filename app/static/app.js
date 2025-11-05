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

  // Interceptar el formulario de registro manual (si existe)
  const manualForm = document.querySelector('form[action="/admin/fichajes/manual"]');
  if (manualForm) {
    manualForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const formData = new FormData(manualForm);
      const rfid = formData.get('rfid_uid');
      if (!rfid || rfid.trim() === '') return alert('Introduce un RFID');

      fetch('/admin/fichajes/manual_ajax', {
        method: 'POST',
        body: formData,
      }).then(resp => resp.json()).then(data => {
        if (!data) return alert('Respuesta inválida');
        if (!data.success) return alert(data.error || 'Error');

        // mostrar flash
        const flash = document.getElementById('flash');
        if (flash) {
          flash.textContent = data.mensaje || 'Registrado';
          flash.className = 'flash success';
        }

        // añadir la nueva fila al inicio de la tabla de recientes si existe
        const tableBody = document.querySelector('.recent-fichajes table tbody');
        if (tableBody && data.fichaje) {
          const tr = document.createElement('tr');
          const ts = document.createElement('td');
          ts.textContent = new Date(data.fichaje.timestamp).toLocaleString();
          const emp = document.createElement('td');
          emp.textContent = data.fichaje.empleado_nombre || data.fichaje.empleado_id;
          const tipo = document.createElement('td');
          tipo.textContent = data.fichaje.tipo;
          tr.appendChild(ts);
          tr.appendChild(emp);
          tr.appendChild(tipo);
          if (tableBody.firstChild) tableBody.insertBefore(tr, tableBody.firstChild);
          else tableBody.appendChild(tr);
        }

        // limpiar input
        manualForm.querySelector('input[name="rfid_uid"]').value = '';
      }).catch(err => {
        console.error(err);
        alert('Error de conexión al registrar');
      });
    });
  }
});
