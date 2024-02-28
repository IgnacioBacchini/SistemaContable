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
        }, 3000); 
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

        const inversorCheckbox = formulario.querySelector('#inversor_prestamista_deudor_T_F');
        const rolSelect = formulario.querySelector('#rol_financiero');
        const idInversorPrestamistaDeudor = formulario.querySelector('#id_inversor_prestamista_deudor');
        const tipoCta = formulario.querySelector('#tipo_cta');
        const idContrato = formulario.querySelector('#id_contrato');

        // Mostrar todos los campos para el formulario "cuenta" y aplicar condiciones específicas
        if (formularioId === 'cuenta') {
            modalContent.innerHTML += `<strong>Nombre de la Cuenta:</strong> ${document.querySelector('#nombre_cuenta').value}<br>`;
            modalContent.innerHTML += `<strong>Empresa:</strong> ${document.getElementById('id_empresa').options[document.getElementById('id_empresa').selectedIndex].text}<br>`;
            modalContent.innerHTML += `<strong>Concepto:</strong> ${document.getElementById('id_concepto').options[document.getElementById('id_concepto').selectedIndex].text}<br>`;
            modalContent.innerHTML += `<strong>Moneda:</strong> ${document.getElementById('id_moneda').options[document.getElementById('id_moneda').selectedIndex].text}<br>`;
            // Si el checkbox "inversor_prestamista_deudor_T_F" está marcado, mostrar "Sí", de lo contrario, mostrar "No"
            const inversorValue = inversorCheckbox.checked ? 'Sí' : 'No';
            modalContent.innerHTML += `<strong>¿Agente Financiero?:</strong> ${inversorValue}<br>`;

            // Si está marcado como inversor, mostrar los campos "Rol Financiero" e "ID Inversor Prestamista Deudor"
            if (inversorCheckbox.checked) {
                modalContent.innerHTML += `<strong>Rol Financiero: </strong> ${rolSelect.value}<br>`;
                modalContent.innerHTML += `<strong>Nombre:</strong> ${idInversorPrestamistaDeudor.options[idInversorPrestamistaDeudor.selectedIndex].text}<br>`;

                // Si el ID Inversor Prestamista Deudor coincide con "Inversor", mostrar los campos "Tipo de Cuenta" e "ID de Contrato"
                if (rolSelect.value === 'Inversor') {
                    modalContent.innerHTML += `<strong>Tipo de Cuenta:</strong> ${tipoCta.value}<br>`;
                    modalContent.innerHTML += `<strong>Contrato:</strong> ${idContrato.options[idContrato.selectedIndex].text}<br>`;
                }
            }
        } else {
            // Mostrar siempre todos los campos para formularios que no son "cuenta"
            const inputs = formulario.querySelectorAll('input[data-label], select[data-label], textarea[data-label]');
            inputs.forEach(input => {
                const label = input.getAttribute('data-label');
                let value = input.value;
                
                // Si el campo es un checkbox, determinar su estado y establecer el valor correspondiente
                if (input.type === 'checkbox') {
                    value = input.checked ? 'Sí' : 'No';
                }
                
                // Si el campo es un <select>, obtenemos el texto de la opción seleccionada
                if (input.tagName === 'SELECT') {
                    const selectedOption = input.options[input.selectedIndex];
                    value = selectedOption.text; // Obtenemos el texto de la opción seleccionada
                }
                
                // Mostrar siempre todos los campos
                modalContent.innerHTML += `<strong>${label}:</strong> ${value}<br>`;
            });
        }

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
