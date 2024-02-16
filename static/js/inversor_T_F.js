function toggleInversorField() {
    var inversorCheckbox = document.getElementById('inversor_prestamista_deudor_T_F');
    var inversorField = document.getElementById('inversorField');
    var tipoCtaField = document.getElementById('tipoCtaField');
    var idContratoField = document.getElementById('contratoField');

    if (inversorCheckbox.checked) {
        inversorField.style.display = 'block';
        tipoCtaField.style.display = 'block';
        idContratoField.style.display = 'block';
    } else {
        inversorField.style.display = 'none';
        tipoCtaField.style.display = 'none';
        idContratoField.style.display = 'none';
    }
}

// Llamada inicial para establecer el estado correcto en la carga de la página
toggleInversorField();