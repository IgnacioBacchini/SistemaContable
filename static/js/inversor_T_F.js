function toggleInversorField() {
    var inversorCheckbox = document.getElementById('inversor_T_F');
    var inversorField = document.getElementById('inversorField');

    if (inversorCheckbox.checked) {
        inversorField.style.display = 'block';
        document.getElementById('id_inversor').required = true;
    } else {
        inversorField.style.display = 'none';
        document.getElementById('id_inversor').required = false;
    }
}

// Llamada inicial para establecer el estado correcto en la carga de la página
toggleInversorField();