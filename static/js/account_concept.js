// account_concept.js

// Variable para almacenar la última solicitud en curso
let currentRequest = null;

// Función para obtener cuentas según el concepto y la cuenta seleccionados
function updateCuentas() {
    var selectedCuentaDesde = document.getElementById('id_cuenta_desde').value;
    var selectedConceptoDesde = document.getElementById('id_concepto_desde').value;
    var selectedEmpresa = document.getElementById('id_empresa').value;
    var selectedMonedaDesde = document.getElementById('id_moneda_desde').value;

    var selectedCuentaHacia = document.getElementById('id_cuenta_hacia').value;
    var selectedConceptoHacia = document.getElementById('id_concepto_hacia').value;
    var selectedMonedaHacia = document.getElementById('id_moneda_hacia').value;

    // Cancelar la solicitud actual si existe
    if (currentRequest) {
        currentRequest.abort();
    }

    // Realizar solicitud AJAX para obtener las cuentas desde
    currentRequest = fetch('/api/get_cuentas', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'id_concepto': selectedConceptoDesde,
            'id_cuenta': selectedCuentaDesde,
            'id_empresa': selectedEmpresa,
            'id_moneda': selectedMonedaDesde
        })
    })
    .then(response => response.json())
    .then(data => {
        // Limpiar y actualizar la lista de cuentas desde
        var cuentaDesdeSelect = document.getElementById('id_cuenta_desde');
        cuentaDesdeSelect.innerHTML = '';

        // Agregar las nuevas opciones
        data.forEach(cuenta => {
            var option = document.createElement('option');
            option.value = cuenta.id_cuenta;
            option.text = cuenta.nombre_cuenta;
            cuentaDesdeSelect.add(option);
        });

        // Seleccionar la cuenta desde original si aún está disponible
        cuentaDesdeSelect.value = selectedCuentaDesde;
    })
    .catch(error => {
        console.error('Error fetching cuentas desde:', error);
    })
    .finally(() => {
        currentRequest = null;
    });

    // Realizar solicitud AJAX para obtener las cuentas hacia
    fetch('/api/get_cuentas_hacia', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'id_concepto_hacia': selectedConceptoHacia,
            'id_empresa_hacia': selectedEmpresa,
            'id_moneda_hacia': selectedMonedaHacia
        })
    })
    .then(response => response.json())
    .then(data => {
        // Limpiar y actualizar la lista de cuentas hacia
        var cuentaHaciaSelect = document.getElementById('id_cuenta_hacia');
        cuentaHaciaSelect.innerHTML = '';

        // Agregar las nuevas opciones
        data.forEach(cuenta => {
            var option = document.createElement('option');
            option.value = cuenta.id_cuenta;
            option.text = cuenta.nombre_cuenta;
            cuentaHaciaSelect.add(option);
        });

        // Seleccionar la cuenta hacia original si aún está disponible
        cuentaHaciaSelect.value = selectedCuentaHacia;
    })
    .catch(error => {
        console.error('Error fetching cuentas hacia:', error);
    });
}

// Llama a la función al cargar la página para cargar las opciones iniciales
document.addEventListener("DOMContentLoaded", function () {
    // Resto del código...

    // Agregar eventos onchange a los elementos de selección de empresa, moneda, conceptos y cuentas
    var empresaSelect = document.getElementById('id_empresa');
    empresaSelect.addEventListener('change', function () {
        handleEmpresaChange();
    });

    var monedaDesdeSelect = document.getElementById('id_moneda_desde');
    monedaDesdeSelect.addEventListener('change', function () {
        handleMonedaChange();
    });

    var monedaHaciaSelect = document.getElementById('id_moneda_hacia');
    monedaHaciaSelect.addEventListener('change', function () {
        handleMonedaChange();
    });

    var conceptoDesdeSelect = document.getElementById('id_concepto_desde');
    conceptoDesdeSelect.addEventListener('change', function () {
        updateCuentas();
    });

    var cuentaDesdeSelect = document.getElementById('id_cuenta_desde');
    cuentaDesdeSelect.addEventListener('change', function () {
        updateCuentas();
    });

    var conceptoHaciaSelect = document.getElementById('id_concepto_hacia');
    conceptoHaciaSelect.addEventListener('change', function () {
        updateCuentas();
    });

    var cuentaHaciaSelect = document.getElementById('id_cuenta_hacia');
    cuentaHaciaSelect.addEventListener('change', function () {
        updateCuentas();
    });

    // Llama a la función al cargar la página para cargar las opciones iniciales
    updateCuentas();
});
