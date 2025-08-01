document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("uploadForm");
  const copyBtn = document.getElementById("copyBtn");
  const shareLink = document.getElementById("shareLink");
  const toast = document.getElementById("toast");
  const progressContainer = document.getElementById("progressContainer");
  const progressText = document.getElementById("progressText");
  const progressBar = document.getElementById("progressBar");

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      progressContainer.style.display = "block";
      progressText.textContent = "Uploading...";

      try {
        const response = await fetch("/", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const error = await response.json();
          progressText.textContent = error.error || "Upload failed.";
          return;
        }

        const result = await response.json();
        window.location.href = result.success_url;
      } catch (err) {
        progressText.textContent = "An error occurred during upload.";
      }
    });
  }

  if (copyBtn && shareLink && toast) {
    copyBtn.addEventListener("click", () => {
      shareLink.select();
      shareLink.setSelectionRange(0, 99999);
      try {
        const successful = document.execCommand("copy");
        if (successful) {
          toast.style.visibility = "visible";
          setTimeout(() => {
            toast.style.visibility = "hidden";
          }, 1800);
        } else {
          alert("Failed to copy link. Please copy manually.");
        }
      } catch (err) {
        alert("Browser does not support copy command. Please copy manually.");
      }
    });
  }
});
