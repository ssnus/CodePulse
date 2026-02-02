document.addEventListener("DOMContentLoaded", () => {
  const els = document.querySelectorAll(".stat-card, .pool-card");
  if (!els.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  els.forEach((el) => observer.observe(el));
});

