// Превью файла в форме создания/редактирования поста
document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('id_attachments');
    if (!fileInput) return;

    fileInput.addEventListener('change', function (e) {
        const file = e.target.files[0];
        const preview = document.getElementById('image-preview');
        const previewImg = document.getElementById('preview-img');

        if (!preview || !previewImg) return;

        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function (event) {
                previewImg.src = event.target.result;
                previewImg.style.display = 'block';
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        } else if (file) {
            previewImg.style.display = 'none';
            preview.style.display = 'block';
        } else {
            preview.style.display = 'none';
            previewImg.style.display = 'none';
        }
    });
});

