document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('modal');
    const closeBtn = document.getElementsByClassName('close')[0];
    const confirmBtn = document.getElementById('confirmar');
    const mensajeExito = document.getElementById('mensaje-exito');

    // Función para mostrar el mensaje de éxito
    function mostrarMensajeExito() {
        mensajeExito.style.display = 'block';
        // Ocultar el mensaje después de unos segundos (opcional)
        setTimeout(function () {
            mensajeExito.style.display = 'none';
        }, 30000); 
    }

    // Escuchar clics en los botones de envío de los formularios
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const formId = this.getAttribute('data-form-id');
            mostrarConfirmacion(formId);
        });
    });

    // Función para mostrar la confirmación
    function mostrarConfirmacion(formularioId) {
        modal.style.display = 'block';
        
        // Obtener los valores del formulario
        const formulario = document.getElementById(formularioId);
        const modalContent = document.getElementById('modal-content');
        modalContent.innerHTML = '';
    
        const inputs = formulario.querySelectorAll('input[data-label], select[data-label], textarea[data-label]');
        let mostrarCamposAdicionales = false; // Bandera para controlar si se deben mostrar los campos adicionales

        inputs.forEach(input => {
            const label = input.getAttribute('data-label');
            let value = input.value;
            
            // Si el campo es un checkbox, determinar su estado y establecer la bandera correspondiente
            if (input.type === 'checkbox') {
                value = input.checked ? 'Sí' : 'No';
                mostrarCamposAdicionales = input.checked; // Establecer la bandera en verdadero si el checkbox está marcado
            }
            
            // Si el campo es un <select>, obtenemos el texto de la opción seleccionada
            if (input.tagName === 'SELECT') {
                const selectedOption = input.options[input.selectedIndex];
                value = selectedOption.text; // Obtenemos el texto de la opción seleccionada
            }
            
            // Mostrar solo si la bandera mostrarCamposAdicionales es verdadera
            if (!mostrarCamposAdicionales && ['id_inversor_prestamista_deudor', 'tipo_cta', 'id_contrato'].includes(input.id)) {
                return; // Salir de la iteración si no se deben mostrar los campos adicionales
            }

            modalContent.innerHTML += `<strong>${label}:</strong> ${value}<br>`;
        });
    
        // Si el usuario confirma, envía el formulario
        confirmBtn.onclick = function () {
            formulario.submit();
            mostrarMensajeExito(); // Llama a la función para mostrar el mensaje de éxito
        }
    }

    // Cerrar el modal al hacer clic en el botón de cierre
    closeBtn.onclick = function () {
        modal.style.display = 'none';
    }

    // Cerrar el modal al hacer clic fuera de él
    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});