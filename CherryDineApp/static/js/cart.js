document.addEventListener('DOMContentLoaded', function () {
    // Обработка удаления из корзины
    document.querySelectorAll('.remove-from-cart').forEach(button => {
        button.addEventListener('click', function () {
            const itemId = this.getAttribute('data-item-id');

            fetch(`/cart/remove/${itemId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification(data.message, 'success');
                        // Удаляем строку из таблицы
                        this.closest('tr').remove();
                        // Обновляем общую сумму
                        updateCartTotal();
                    } else {
                        showNotification(data.message, 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Произошла ошибка при удалении из корзины', 'danger');
                });
        });
    });

    // Обработка изменения количества
    document.querySelectorAll('.increase-quantity').forEach(button => {
        button.addEventListener('click', function () {
            const itemId = this.getAttribute('data-item-id');
            const quantityInput = this.parentElement.querySelector('.item-quantity');
            const currentQuantity = parseInt(quantityInput.value);

            updateQuantity(itemId, currentQuantity + 1);
        });
    });

    document.querySelectorAll('.decrease-quantity').forEach(button => {
        button.addEventListener('click', function () {
            const itemId = this.getAttribute('data-item-id');
            const quantityInput = this.parentElement.querySelector('.item-quantity');
            const currentQuantity = parseInt(quantityInput.value);

            if (currentQuantity > 1) {
                updateQuantity(itemId, currentQuantity - 1);
            }
        });
    });

// Функция форматирования цены
    function formatPrice(price) {
        // Округляем до 2 знаков после запятой
        const roundedPrice = Number(price).toFixed(2);
        // Если число целое, убираем десятичную часть
        const formattedPrice = roundedPrice.endsWith('.00')
            ? Math.floor(price)
            : roundedPrice;
        return `${formattedPrice}`;
    }

    function updateQuantity(itemId, newQuantity) {
        fetch(`/cart/update/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                quantity: newQuantity
            })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка обновления количества');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    const row = document.querySelector(`[data-item-id="${itemId}"]`).closest('tr');
                    row.querySelector('.item-quantity').value = newQuantity;
                    row.querySelector('td:nth-child(4)').textContent = `${formatPrice(data.subtotal)} ₽`;
                    updateCartTotal();
                    showNotification('Количество обновлено', 'success');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Произошла ошибка при обновлении количества', 'danger');
            });
    }

    function updateCartTotal() {
        const totalElement = document.querySelector('#cart-total');
        if (!totalElement) return;

        const total = Array.from(document.querySelectorAll('tr')).reduce((sum, row) => {
            const subtotalCell = row.querySelector('td:nth-child(4)');
            if (!subtotalCell) return sum;

            const subtotalText = subtotalCell.textContent;
            const subtotal = parseFloat(subtotalText.replace(/[₽\s]/g, ''));
            return sum + (isNaN(subtotal) ? 0 : subtotal);
        }, 0);

        totalElement.textContent = formatPrice(total);
    }
});