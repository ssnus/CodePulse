document.addEventListener("DOMContentLoaded", () => {
  const contentField = document.querySelector(".feed-compose-card textarea");
  if (contentField) {
    const resize = () => {
      contentField.style.height = "auto";
      contentField.style.height = contentField.scrollHeight + "px";
    };
    contentField.addEventListener("input", resize);
    resize();
  }

  document.querySelectorAll(".js-toggle-comment").forEach((btn) => {
    btn.addEventListener("click", () => {
      const postId = btn.dataset.postId;
      const form = document.querySelector(
        `.post-comment-form[data-post-id="${postId}"]`
      );
      if (form) {
        form.classList.toggle("d-none");
        const textarea = form.querySelector("textarea");
        if (!form.classList.contains("d-none") && textarea) {
          textarea.focus();
        }
      }
    });
  });

  const fileInput = document.querySelector(".feed-attachments-input");
  const attachText = document.querySelector(".js-attach-text");
  if (fileInput && attachText) {
    fileInput.addEventListener("change", () => {
      if (!fileInput.files || fileInput.files.length === 0) {
        attachText.textContent = "Вложение";
      } else if (fileInput.files.length === 1) {
        const name = fileInput.files[0].name;
        attachText.textContent = name.length > 20 ? "1 файл" : name;
      } else {
        attachText.textContent = `${fileInput.files.length} файлов`;
      }
    });
  }
});