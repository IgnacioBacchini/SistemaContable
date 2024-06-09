// Variable para almacenar la última solicitud en curso
let currentRequest = null;

// Función para obtener contratos según el agente seleccionado
function updateContratos() {
    var selectedAgente = document.getElementById('id_inversor_prestamista_deudor').value;

    // Cancelar la solicitud actual si existe
    if (currentRequest) {
        currentRequest.abort();
    }

    // Realizar solicitud AJAX para obtener los contratos
    currentRequest = fetch('/api/get_contratos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'id_inversor_prestamista_deudor': selectedAgente })
    })
    .then(response => response.json())
    .then(data => {
        // Limpiar y actualizar la lista de contratos
        var contratoSelect = document.getElementById('id_contrato');
        contratoSelect.innerHTML = '';

        // Agregar la opción "Seleccione contrato" nuevamente
        var optionSeleccione = document.createElement('option');
        optionSeleccione.value = "";
        optionSeleccione.textContent = "Seleccione contrato";
        contratoSelect.appendChild(optionSeleccione);

        // Agregar las nuevas opciones
        data.forEach(contrato => {
            var option = document.createElement('option');
            option.value = contrato.id_contrato;
            // Formatear la fecha
            var fechaFinObra = new Date(contrato.proyecto.fecha_fin_obra);
            var dia = String(fechaFinObra.getDate() + 1).padStart(2, '0');
            var mes = String(fechaFinObra.getMonth() + 1).padStart(2, '0'); // Enero es 0
            var año = fechaFinObra.getFullYear();
            var fechaFormateada = `${dia}-${mes}-${año}`;

            // Establecer el texto del contrato con la fecha formateada
            option.text = `${contrato.nombre_contrato} (Fin de proyecto: ${fechaFormateada})`;
            contratoSelect.add(option);
        });

        // Deshabilitar la opción "Seleccione contrato"
        optionSeleccione.disabled = true;
    })
    .catch(error => {
        console.error('Error fetching contratos:', error);
    })
    .finally(() => {
        currentRequest = null;
    });
}

// Llama a la función al cargar la página para cargar las opciones iniciales
document.addEventListener("DOMContentLoaded", function () {
    // Agregar evento onchange al elemento de selección de agente
    var agenteSelect = document.getElementById('id_inversor_prestamista_deudor');
    agenteSelect.addEventListener('change', function () {
        updateContratos();
    });

    // Llamar a la función para cargar las opciones iniciales
    updateContratos();
});
