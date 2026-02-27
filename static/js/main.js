// Показать/скрыть пароль
document.addEventListener('DOMContentLoaded', function() {
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');

    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = document.querySelector(this.getAttribute('data-target'));
            const icon = this.querySelector('i');

            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            }
        });
    });

    // Подтверждение удаления
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить?')) {
                e.preventDefault();
            }
        });
    });

    // Авто-ресайз текстареа
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });
});

$(document).ready(function() {
    const $input = $('#search-input');
    const $dropdown = $('#search-results-dropdown');
    let debounceTimer;

    $input.on('input', function() {
        clearTimeout(debounceTimer);

        const query = $.trim($(this).val());

        if (query.length < 2) {
            $dropdown.addClass('d-none').empty();
            return;
        }

        debounceTimer = setTimeout(function() {
            $.ajax({
                url: '/search/',
                type: 'GET',
                data: { q: query },
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                success: function(data) {
                    $dropdown.empty();

                    if (data.results && data.results.length > 0) {
                        data.results.forEach(function(item) {
                            const itemHtml = `
                                <a href="${item.url}" class="list-group-item list-group-item-action bg-dark text-white border-secondary d-flex align-items-center">
                                    <i class="bi ${item.icon} me-3 fs-4 text-primary"></i>
                                    <div>
                                        <small class="text-muted">${item.type}</small>
                                        <div class="fw-bold">${item.title}</div>
                                    </div>
                                </a>
                            `;
                            $dropdown.append(itemHtml);
                        });

                        const moreLink = `
                            <a href="/search/?q=${encodeURIComponent(query)}"
                               class="list-group-item list-group-item-action bg-primary text-white text-center py-3 fw-bold">
                                <i class="bi bi-search me-2"></i> Показать все результаты
                            </a>
                        `;
                        $dropdown.append(moreLink);

                        $dropdown.removeClass('d-none');
                    } else {
                        $dropdown.html('<div class="list-group-item bg-dark text-muted text-center py-3">Ничего не найдено</div>')
                                 .removeClass('d-none');
                    }
                },
                error: function() {
                    $dropdown.html('<div class="list-group-item bg-danger text-white text-center py-3">Ошибка поиска</div>')
                             .removeClass('d-none');
                }
            });
        }, 300);
    });

    $(document).on('click', function(e) {
        if (!$(e.target).closest('#search-form, #search-results-dropdown').length) {
            $dropdown.addClass('d-none');
        }
    });

    $dropdown.on('click', function(e) {
        e.stopPropagation();
    });
});