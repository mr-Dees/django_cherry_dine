document.addEventListener('DOMContentLoaded', function () {
    // Обработка изменения количества товара
    document.querySelectorAll('.decrease-quantity, .increase-quantity').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const input = this.closest('.input-group').querySelector('.item-quantity');
            let currentValue = parseInt(input.value);

            if (this.classList.contains('decrease-quantity') && currentValue > 1) {
                input.value = currentValue - 1;
            } else if (this.classList.contains('increase-quantity') && currentValue < 99) {
                input.value = currentValue + 1;
            }
        });
    });

    // Обработка добавления в корзину
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const dishId = this.getAttribute('data-dish-id');
            const quantityInput = this.closest('.d-flex').querySelector('.item-quantity');
            const quantity = parseInt(quantityInput ? quantityInput.value : 1);

            this.disabled = true;
            this.innerHTML = 'Добавление...';

            fetch(`/cart/add/${dishId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    quantity: quantity
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification(data.message, 'success', true);
                        // Заменяем кнопки на "Перейти в корзину"
                        const container = this.closest('.d-flex');
                        container.innerHTML = `
                        <a href="/cart/" class="btn btn-primary">
                            Перейти в корзину
                        </a>
                    `;

                        const cartCounter = document.querySelector('.cart-counter');
                        if (cartCounter) {
                            cartCounter.textContent = data.cart_total;
                        }
                    } else {
                        showNotification(data.message, 'danger', true);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Произошла ошибка при добавлении в корзину', 'danger', true);
                });
        });
    });
});