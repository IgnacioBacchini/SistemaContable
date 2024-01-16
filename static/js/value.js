function updateValueTo() {
    var valueFrom = parseFloat(document.getElementById('valor_desde').value) || 0;
    var exchangeRate = parseFloat(document.getElementById('tipo_de_cambio').value) || 1;

    var valueTo = valueFrom * exchangeRate;
    // Actualiza el campo de solo lectura y el campo en el formulario
    document.getElementById('valor_hacia_calculado').value = valueTo.toFixed(2);
    // Si deseas enviar el valor calculado al servidor, puedes agregar un campo oculto aquí
}