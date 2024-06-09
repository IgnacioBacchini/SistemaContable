document.addEventListener("DOMContentLoaded", function () {
    var rolSelect = document.getElementById('inversor_o_prestamista_o_deudor');
    rolSelect.addEventListener('change', function () {
        // console.log('Role changed to:', rolSelect.value);  // Verifica que el evento se dispara
        updateAgentes();
    });

    // Llamar a la función para cargar las opciones iniciales
    updateAgentes();
});

function updateAgentes() {
    var selectedRol = document.getElementById('inversor_o_prestamista_o_deudor').value;

    // console.log('Selected role:', selectedRol);  // Verifica el rol seleccionado

    // Cancelar la solicitud actual si existe
    if (currentRequest) {
        currentRequest.abort();
    }

    // Realizar solicitud AJAX para obtener los agentes
    currentRequest = fetch('/api/get_investor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'inversor_o_prestamista_o_deudor': selectedRol })
    })
    .then(response => {
        // console.log('Response received:', response);  // Verifica que se recibe la respuesta
        return response.json();
    })
    .then(data => {
        // console.log('Data received:', data);  // Verifica los datos recibidos
        // Limpiar y actualizar la lista de agentes
        var agenteSelect = document.getElementById('id_inversor_prestamista_deudor');
        agenteSelect.innerHTML = '';

        // Agregar la opción "Seleccione agente" nuevamente
        var optionSeleccione = document.createElement('option');
        optionSeleccione.value = "";
        optionSeleccione.textContent = "Seleccione agente";
        agenteSelect.appendChild(optionSeleccione);

        // Agregar las nuevas opciones
        data.forEach(agente => {
            var option = document.createElement('option');
            option.value = agente.id_inversor_prestamista_deudor;
            option.text = agente.nombre_inversor_prestamista_deudor;
            agenteSelect.add(option);
        });

        // Deshabilitar la opción "Seleccione agente"
        optionSeleccione.disabled = true;
    })
    .catch(error => {
        // console.error('Error fetching agentes:', error);
    })
    .finally(() => {
        currentRequest = null;
    });
}
