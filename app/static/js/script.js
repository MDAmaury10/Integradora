$(document).ready(function() {
    $('#venta-form').on('submit', function(event) {
        event.preventDefault();  // Prevenir el comportamiento predeterminado del formulario

        var productos = [];
        $('#productos-container .producto-item').each(function() {
            var producto = $(this).find('.producto').val();
            var cantidad = $(this).find('.cantidad').val();
            productos.push({ 'producto': producto, 'cantidad': cantidad });
        });

        var data = {
            user_id: $('input[name="user_id"]').val(),
            total: $('#total').val(),
            efectivo: $('#efectivo').val(),
            cambio: $('#cambio').val(),
            productos: productos
        };

        $.ajax({
            url: "{{ url_for('ventas_nuevo') }}",
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                // Maneja la respuesta exitosa
                window.location.href = "{{ url_for('ventas') }}";  // Redirigir a la página de ventas
            },
            error: function(xhr) {
                // Maneja los errores
                alert('Error al registrar la venta');
            }
        });
    });
});
