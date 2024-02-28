function toggleInversorField() {
    var inversorCheckbox = document.getElementById('inversor_prestamista_deudor_T_F');
    var rolField = document.getElementById('rolField');
    var inversorField = document.getElementById('inversorField');
    var tipoCtaField = document.getElementById('tipoCtaField');
    var idContratoField = document.getElementById('contratoField');
    var rolValue = document.getElementById('rol_financiero').value;

    if (inversorCheckbox.checked) {
        rolField.style.display = 'block';
        inversorField.style.display = 'block';
        tipoCtaField.style.display = 'block';
        idContratoField.style.display = 'block';
    } else {
        rolField.style.display = 'none';
        inversorField.style.display = 'none';
        tipoCtaField.style.display = 'none';
        idContratoField.style.display = 'none';
    }
}

// Llamada inicial para establecer el estado correcto en la carga de la página
toggleInversorField();

// Agregar eventos change al campo 'rolField' y a la casilla de verificación 'inversor_prestamista_deudor_T_F'
document.getElementById('rolField').addEventListener('change', function() {
    toggleInversorField();
});

document.getElementById('inversor_prestamista_deudor_T_F').addEventListener('change', function() {
    toggleInversorField();
});
