document.addEventListener("DOMContentLoaded", () => {
  const copyBtn = document.getElementById("copyBtn");
  const shareLink = document.getElementById("shareLink");
  const toast = document.getElementById("toast");

  copyBtn.addEventListener("click", () => {
    shareLink.select();
    shareLink.setSelectionRange(0, 99999);
    try {
      const successful = document.execCommand("copy");
      if (successful) {
        showToast();
      } else {
        alert("Failed to copy link. Please copy manually.");
      }
    } catch (err) {
      alert("Browser does not support copy command. Please copy manually.");
    }
  });

  function showToast() {
    toast.style.visibility = "visible";
    setTimeout(() => {
      toast.style.visibility = "hidden";
    }, 1800);
  }
});
