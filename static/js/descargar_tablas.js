function descargarCSV(tablas, nombreArchivo) {
    var datos = [];
    tablas.forEach(function(tablaID) {
        var tabla = $('#' + tablaID).DataTable();
        var tablaData = tabla.data().toArray();
        datos = datos.concat(tablaData);
    });

    var csv = "";
    var cabeceras = $('#' + tablas[0] + ' th').map(function() {
        return $(this).text();
    }).get();
    csv += cabeceras.join(",") + "\n";

    datos.forEach(function(fila) {
        csv += fila.join(",") + "\n";
    });

    var blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    if (navigator.msSaveBlob) { // IE 10+
        navigator.msSaveBlob(blob, nombreArchivo + ".csv");
    } else {
        var link = document.createElement("a");
        if (link.download !== undefined) { // feature detection
            var url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", nombreArchivo + ".csv");
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
}