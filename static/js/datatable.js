$(document).ready(function () {
    $('.dataTable').DataTable({
        "language": {
            "emptyTable": "No hay datos disponibles en la tabla",
            "search": "Buscar ",
            "lengthMenu": "Filas a mostrar: _MENU_",
            "paginate": {
                "previous": "Anterior",
                "next": "Siguiente"
            },
            "info": "Mostrando _START_ a _END_ de _TOTAL_ entradas"
        },
        "scrollX": false,
        "order": [[0, "asc"]],
        "lengthMenu": [5, 10, 25, 50]
    });
});