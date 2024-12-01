// Глобальная переменная для состояния звука
let isSoundEnabled = localStorage.getItem('soundEnabled') !== 'false';

// Функция для получения CSRF токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Функция воспроизведения звука
function playNotificationSound() {
    if (!isSoundEnabled) return;

    const audio = document.getElementById('notification-sound');
    if (audio) {
        audio.volume = 0.125;
        audio.currentTime = 0;
        audio.play().catch(error => console.error('Ошибка воспроизведения:', error));
    }
}

// Функция показа уведомлений
function showNotification(message, type = 'success') {
    const container = document.getElementById('notification-container');

    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    container.appendChild(notification);
    playNotificationSound();

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 150);
    }, 5000);
}

// Основной код при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
    // Инициализация управления звуком
    const soundToggle = document.getElementById('sound-toggle');
    const soundIcon = soundToggle.querySelector('i');

// Инициализация тултипов Bootstrap с автоматическим скрытием
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'hover',    // Показывать только при наведении
            html: true,          // Разрешаем HTML в подсказке
            delay: {             // Задержки появления/исчезновения
                show: 0,         // Показывать сразу
                hide: 0          // Скрывать сразу
            }
        });
    });

    // Установка начального состояния звука
    function updateSoundToggleState() {
        if (isSoundEnabled) {
            soundIcon.className = 'fas fa-volume-up';
            soundToggle.setAttribute('data-bs-original-title', 'Выключить звук уведомлений');
        } else {
            soundIcon.className = 'fas fa-volume-mute';
            soundToggle.setAttribute('data-bs-original-title', 'Включить звук уведомлений');
        }
        const tooltip = bootstrap.Tooltip.getInstance(soundToggle);
        if (tooltip) {
            tooltip.update();
        }
    }

    updateSoundToggleState();

    // Обработчик переключения звука
    soundToggle.addEventListener('click', function () {
        isSoundEnabled = !isSoundEnabled;
        localStorage.setItem('soundEnabled', isSoundEnabled);
        updateSoundToggleState();
    });

    // Обработка существующих уведомлений Django messages
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        playNotificationSound();
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => {
                alert.remove();
            }, 150);
        }, 5000);
    });

    // Обработка кнопок добавления в корзину
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function () {
            const dishId = this.getAttribute('data-dish-id');

            this.classList.add('disabled');
            this.innerHTML = 'Добавление...';

            fetch(`/cart/add/${dishId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification(data.message, 'success');

                        const cartCounter = document.querySelector('.cart-counter');
                        if (cartCounter) {
                            cartCounter.textContent = data.cart_total;
                        }
                    } else {
                        showNotification(data.message, 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Произошла ошибка при добавлении в корзину', 'danger');
                })
                .finally(() => {
                    this.classList.remove('disabled');
                    this.innerHTML = 'В корзину';
                });
        });
    });
});