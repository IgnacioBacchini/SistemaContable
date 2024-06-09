// confirm_form.js

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

    // Construir mensaje de confirmación con los valores seleccionados
    var mensajeConfirmacion = "¿Desea añadir los siguientes datos?\n\n";
    formData.forEach(function(valor, clave) {
        var etiquetaCampo = form.querySelector('[name="' + clave + '"]').getAttribute('data-label');
        var campoSeleccionado = form.querySelector('[name="' + clave + '"] option[value="' + valor + '"]');
        var textoSeleccionado = campoSeleccionado ? campoSeleccionado.textContent : valor;
        mensajeConfirmacion += etiquetaCampo + ": " + textoSeleccionado + "\n";
    });

    // Mostrar ventana de confirmación
    var confirmacion = confirm(mensajeConfirmacion);
    return confirmacion;
}

// Asignar la función validarFormulario a los botones de envío de los formularios
document.addEventListener('DOMContentLoaded', function() {
    var formularios = document.querySelectorAll('form');
    formularios.forEach(function(form) {
        var formId = form.getAttribute('id');
        var submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.addEventListener('click', function(event) {
                event.preventDefault(); // Prevenir el envío automático del formulario
                var formValidado = validarFormulario(formId);
                if (formValidado) {
                    form.submit(); // Enviar el formulario si fue validado
                }
            });
        }
    });
});
