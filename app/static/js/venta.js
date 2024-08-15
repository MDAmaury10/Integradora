document.addEventListener('DOMContentLoaded', function() {
    // Obtener referencias a los elementos del DOM
    const agregarProductoBtn = document.getElementById('agregar-producto');
    const productosContainer = document.getElementById('productos-container');

    // Función para agregar un nuevo campo de producto y cantidad
    function agregarProducto() {
        // Crear el nuevo elemento del producto
        const nuevoProductoDiv = document.createElement('div');
        nuevoProductoDiv.classList.add('form-group');
        nuevoProductoDiv.innerHTML = `
            <label for="producto">Producto:</label>
            <select class="form-control producto" name="producto[]" required>
                <option value="" disabled selected>Selecciona un producto</option>
                {% for producto in productos %}
                    <option value="{{ producto[0] }}" data-precio="{{ producto[2] }}">{{ producto[1] }}</option>
                {% endfor %}
            </select>
        `;

        // Crear el nuevo elemento de cantidad
        const nuevaCantidadDiv = document.createElement('div');
        nuevaCantidadDiv.classList.add('form-group');
        nuevaCantidadDiv.innerHTML = `
            <label for="cantidad">Cantidad:</label>
            <input type="number" class="form-control cantidad" name="cantidad[]" min="1" required>
        `;

        // Agregar los nuevos elementos al contenedor
        productosContainer.appendChild(nuevoProductoDiv);
        productosContainer.appendChild(nuevaCantidadDiv);

        // Recalcular el total cuando se agregue un nuevo producto
        recalcularTotal();
    }

    // Función para recalcular el total y el cambio
    function recalcularTotal() {
        let total = 0;
        const productos = document.querySelectorAll('.producto');
        const cantidades = document.querySelectorAll('.cantidad');
        productos.forEach((producto, index) => {
            const precio = parseFloat(producto.options[producto.selectedIndex].dataset.precio) || 0;
            const cantidad = parseInt(cantidades[index].value) || 0;
            total += precio * cantidad;
        });
        document.getElementById('total').value = total.toFixed(2);
        calcularCambio();
    }

    // Función para calcular el cambio
    function calcularCambio() {
        const total = parseFloat(document.getElementById('total').value) || 0;
        const efectivo = parseFloat(document.getElementById('efectivo').value) || 0;
        const cambio = efectivo - total;
        document.getElementById('cambio').value = cambio.toFixed(2);
    }

    // Event listeners para los campos de cantidad y efectivo
    productosContainer.addEventListener('change', recalcularTotal);
    document.getElementById('efectivo').addEventListener('input', calcularCambio);
    agregarProductoBtn.addEventListener('click', agregarProducto);
});
