// While a form marked data-busy is waiting for the model, show how long it has been waiting.
document.querySelectorAll("form[data-busy]").forEach((form) => {
  form.addEventListener("submit", () => {
    const button = form.querySelector("button[type=submit]");
    const busy = form.querySelector(".busy");
    const seconds = form.querySelector("[data-seconds]");
    if (button) button.disabled = true;
    if (!busy) return;
    busy.hidden = false;
    const started = Date.now();
    setInterval(() => {
      seconds.textContent = Math.floor((Date.now() - started) / 1000);
    }, 250);
  });
});
