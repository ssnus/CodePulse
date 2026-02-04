$(document).ready(function() {
    const contentField = $(".feed-compose-card textarea");
    if (contentField.length) {
        const resize = function() {
            $(this).css('height', 'auto').css('height', this.scrollHeight + 'px');
        };
        contentField.on('input', resize);
        contentField.each(resize);
    }

    $(document).on('click', '.js-toggle-comment', function() {
        const postId = $(this).data('post-id');
        const form = $(`.post-comment-form[data-post-id="${postId}"]`);
        
        if (form.length) {
            form.toggleClass('d-none');
            const textarea = form.find('textarea');
            if (!form.hasClass('d-none') && textarea.length) {
                textarea.focus();
            }
        }
    });

    // Обновление текста кнопки при выборе файлов
    const fileInput = $('#id_attachments');
    const attachText = $('.js-attach-text');

    if (fileInput.length && attachText.length) {
        fileInput.on('change', function() {
            const files = $(this)[0].files;

            if (!files || files.length === 0) {
                attachText.text('Вложение');
            } else if (files.length === 1) {
                const name = files[0].name;
                attachText.text(name.length > 20 ? '1 файл' : name);
            } else {
                attachText.text(`${files.length} файлов`);
            }
        });
    }

    // ============================================
    // ОТПРАВКА ОСНОВНОЙ ФОРМЫ ПОСТА ЧЕРЕЗ AJAX
    // ============================================
    const mainForm = $('#ajax-post-form');

    if (mainForm.length) {
        mainForm.on('submit', function(e) {
            e.preventDefault();

            const $form = $(this);
            const submitBtn = $form.find('button[type="submit"]');
            const originalBtnText = submitBtn.html();

            // Отладка перед отправкой
            const contentVal = $form.find('textarea[name="content"]').val();
            const fileInput = $form.find('input[type="file"]')[0];
            const files = fileInput ? fileInput.files : null;

            console.log('=== ОТЛАДКА ФОРМЫ ===');
            console.log('Content:', contentVal);
            console.log('Content length:', contentVal ? contentVal.length : 0);
            console.log('Files:', files);
            console.log('Files count:', files ? files.length : 0);
            console.log('CSRF token:', getCookie('csrftoken'));

            if (!contentVal || contentVal.trim().length === 0) {
                alert('Пожалуйста, напишите текст поста!');
                return;
            }

            submitBtn.prop('disabled', true);
            submitBtn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Отправка...');

            const formData = new FormData(this);

            console.log('FormData entries:');
            for (let [key, value] of formData.entries()) {
                if (value instanceof File) {
                    console.log(`  ${key}: File(${value.name}, ${value.size} bytes)`);
                } else {
                    console.log(`  ${key}: ${value}`);
                }
            }

            $.ajax({
                url: $form.attr('action') || window.location.href,
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                success: function(response) {
                    console.log('Успех:', response);

                    if (response.success) {
                        const alertHtml = `
                            <div class="alert alert-success alert-dismissible fade show mt-3" role="alert">
                                ${response.message}
                                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                            </div>
                        `;

                        $form.after(alertHtml);

                        $form[0].reset();
                        $('.js-attach-text').text('Вложение');

                        setTimeout(function() {
                            $('.alert-success').alert('close');
                        }, 3000);

                        // Перезагружаем страницу через 1 секунду
                        setTimeout(function() {
                            window.location.reload();
                        }, 1000);
                    } else {
                        console.log('Ошибки валидации:', response.errors);

                        let errorHtml = `
                            <div class="alert alert-danger alert-dismissible fade show mt-3" role="alert">
                                <strong>Ошибки валидации:</strong>
                                <ul class="mb-0 mt-2">
                        `;

                        $.each(response.errors, function(field, errors) {
                            $.each(errors, function(index, error) {
                                errorHtml += `<li><strong>${field}:</strong> ${error}</li>`;
                            });
                        });

                        errorHtml += `
                                </ul>
                                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                            </div>
                        `;

                        $form.after(errorHtml);

                        setTimeout(function() {
                            $('.alert-danger').alert('close');
                        }, 5000);
                    }
                },
                error: function(xhr, status, error) {
                    console.error('=== ОШИБКА ОТПРАВКИ ===');
                    console.error('Status:', status);
                    console.error('Error:', error);
                    console.error('Response status:', xhr.status);

                    let errorMsg = 'Неизвестная ошибка при отправке';
                    let errorDetails = '';

                    try {
                        const response = JSON.parse(xhr.responseText);
                        console.error('Response JSON:', response);

                        if (response.errors) {
                            errorMsg = 'Ошибка валидации формы';
                            $.each(response.errors, function(field, errors) {
                                errorDetails += `<li><strong>${field}:</strong> ${errors.join(', ')}</li>`;
                            });
                        }
                    } catch (e) {
                        console.error('Parse error:', e);
                        errorMsg = 'Ошибка сервера';
                        errorDetails = xhr.responseText.substring(0, 200);
                    }

                    const alertHtml = `
                        <div class="alert alert-danger alert-dismissible fade show mt-3" role="alert">
                            <strong>${errorMsg}</strong>
                            ${errorDetails ? `<ul class="mt-2">${errorDetails}</ul>` : ''}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    `;

                    $form.after(alertHtml);

                    setTimeout(function() {
                        $('.alert-danger').alert('close');
                    }, 5000);
                },
                complete: function() {
                    submitBtn.prop('disabled', false);
                    submitBtn.html(originalBtnText);
                }
            });
        });
    }

    // ============================================
    // ОТПРАВКА ЛАЙКОВ ЧЕРЕЗ AJAX
    // ============================================
    $(document).on('submit', '.like-form', function(e) {
        e.preventDefault();

        const $form = $(this);
        const $iconSpan = $form.find('.like-icon');
        const $countSpan = $form.find('.like-count');
        const url = $form.attr('action');

        $.ajax({
            type: 'POST',
            url: url,
            data: $form.serialize(),
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function(response) {
                $countSpan.text(response.total_likes);

                if (response.liked) {
                    $iconSpan.html('<i class="bi bi-heart-fill text-danger"></i>');
                } else {
                    $iconSpan.html('<i class="bi bi-heart"></i>');
                }
            },
            error: function(xhr) {
                console.error("Ошибка при отправке лайка:", xhr.statusText);
                alert('Ошибка при отправке лайка. Попробуйте снова.');
            }
        });
    });
});
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