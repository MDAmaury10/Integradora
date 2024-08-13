$(document).ready(function() {
    $('#agregar-producto').click(function() {
        let productIndex = 0; // Contador para los índices de los productos

        // Función para agregar un nuevo par de campos
        function addProductField() {
            productIndex++;
            let newProductGroup = `
                <div class="form-group producto-item">
                    <label for="producto-${productIndex}">Producto:</label>
                    ${$('#producto-template').clone().prop('outerHTML')}
                </div>
                <div class="form-group cantidad-item">
                    <label for="cantidad-${productIndex}">Cantidad:</label>
                    <input id="cantidad-${productIndex}" type="number" class="cantidad" name="cantidad[]" min="1" required>
                </div>`;
            $('#productos-container').append(newProductGroup);
    }
    

// Agregar un nuevo par de campos al hacer clic en el botón
$('#agregar-producto').click(function() {
    addProductField();

});

    // Actualiza el total y cambio al modificar la cantidad o el efectivo
    $('#productos-container').on('change', 'select.producto, input.cantidad', function() {
        updateTotalAndChange();
    });
    
    $('#efectivo').on('input', function() {
        updateTotalAndChange();
    });

    function updateTotalAndChange() {
        let total = 0;
        $('#productos-container .producto-item select').each(function(index) {
            let precio = parseFloat($(this).find('option:selected').data('precio')) || 0;
            let cantidad = parseFloat($('#productos-container .cantidad-item input').eq(index).val()) || 0;
            total += precio * cantidad;
        });

        $('#total').val(total.toFixed(2));

        let efectivo = parseFloat($('#efectivo').val()) || 0;
        let cambio = efectivo - total;
        $('#cambio').val(cambio.toFixed(2));
    }
});