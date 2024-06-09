// Función para validar y confirmar el formulario
function validarFormulario(formId) {
    var form = document.getElementById(formId);
    var formData = new FormData(form);

    // Verificar si hay campos requeridos vacíos
    var camposRequeridos = form.querySelectorAll('[required]');
    for (var i = 0; i < camposRequeridos.length; i++) {
        var campo = camposRequeridos[i];
        var valorCampo = formData.get(campo.name);
        if (!valorCampo || valorCampo.trim() === '') {
            alert("Por favor, complete todos los campos requeridos.");
            return false;
        }
    }

    // Construir mensaje de confirmación con los valores de los campos
    var mensajeConfirmacion = "¿Desea añadir los siguientes datos?\n\n";
    formData.forEach(function(valor, clave) {
        var etiquetaCampo = form.querySelector('[name="' + clave + '"]').getAttribute('data-label');
        var campo = form.querySelector('[name="' + clave + '"]');
        if (campo.tagName === 'SELECT') {
            var opcionSeleccionada = campo.querySelector('option[value="' + valor + '"]');
            valor = opcionSeleccionada ? opcionSeleccionada.textContent : valor;
        }
        mensajeConfirmacion += etiquetaCampo + ": " + valor + "\n";
    });

    // Mostrar ventana de confirmación
    var confirmacion = confirm(mensajeConfirmacion);
    return confirmacion;
}
