function toggleTasaField() {
    var tasaCheckbox = document.getElementById('tasa_T_F');
    var tasaField = document.getElementById('tasaField');

    if (tasaCheckbox.checked) {
        tasaField.style.display = 'block';
        document.getElementById('id_tasa').required = true;
    } else {
        tasaField.style.display = 'none';
        document.getElementById('id_tasa').required = false;
    }
}

// Llamada inicial para establecer el estado correcto en la carga de la página
toggleTasaField();