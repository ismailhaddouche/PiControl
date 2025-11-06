document.addEventListener('DOMContentLoaded', function(){
  // Interceptar envíos AJAX de asignación de RFID si existen botones con data-assign
  document.querySelectorAll('[data-ajax-assign]').forEach(function(btn){
    btn.addEventListener('click', function(e){
      e.preventDefault();
      const employeeId = this.dataset.empid;
      const input = document.querySelector('#rfid-input-' + employeeId);
  if(!input) return alert('RFID field not found');
  const rfid = input.value.trim();
  if(!rfid) return alert('Enter an RFID');
      const url = '/admin/employees/' + employeeId + '/assign_ajax';
      fetch(url, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body: 'rfid_uid=' + encodeURIComponent(rfid)})
        .then(resp => resp.json())
        .then(data => {
          if(data && data.success){
            const flash = document.getElementById('flash');
            flash.textContent = 'RFID assigned to ' + (data.name || data.nombre);
            flash.className = 'flash success';
            // actualizar celda rfid
            const cell = document.querySelector('#rfid-cell-' + employeeId);
            if(cell) cell.textContent = data.rfid_uid || '';
            input.value = '';
            } else {
            alert(data?.error || 'Error assigning RFID');
          }
        }).catch(err => {
          console.error(err);
          alert('Connection error assigning RFID');
        });
    });
  });

  // Interceptar el formulario de registro manual (si existe)
  const manualForm = document.querySelector('form[action="/admin/checkins/manual"]');
  if (manualForm) {
    manualForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const formData = new FormData(manualForm);
      const rfid = formData.get('rfid_uid');
  if (!rfid || rfid.trim() === '') return alert('Enter an RFID');

      fetch('/admin/checkins/manual_ajax', {
        method: 'POST',
        body: formData,
      }).then(resp => resp.json()).then(data => {
        if (!data) return alert('Invalid response');
        if (!data.success) return alert(data.error || 'Error');

        // mostrar flash
        const flash = document.getElementById('flash');
        if (flash) {
          flash.textContent = data.message || 'Registered';
          flash.className = 'flash success';
        }

        // añadir la nueva fila al inicio de la tabla de recientes si existe
  const tableBody = document.querySelector('.recent-checkins table tbody');
        if (tableBody && data.checkin) {
          const tr = document.createElement('tr');
          const ts = document.createElement('td');
          ts.textContent = new Date(data.checkin.timestamp).toLocaleString();
          const emp = document.createElement('td');
          emp.textContent = data.checkin.employee_name || data.checkin.employee_id;
          const tipo = document.createElement('td');
          tipo.textContent = data.checkin.type;
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
        alert('Connection error creating record');
      });
    });
  }
});
