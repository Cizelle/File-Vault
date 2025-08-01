document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("uploadForm");
  const progressBar = document.getElementById("progressBar");
  const progressContainer = document.getElementById("progressContainer");
  const progressText = document.getElementById("progressText");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const xhr = new XMLHttpRequest();
    const formData = new FormData(form);

    progressContainer.style.display = "block";
    progressBar.style.width = "0%";
    progressText.textContent = "0% uploaded";

    xhr.upload.addEventListener("progress", function (event) {
      if (event.lengthComputable) {
        let percent = Math.round((event.loaded / event.total) * 100);
        progressBar.style.width = percent + "%";
        progressText.textContent = percent + "% uploaded";
      }
    });

    xhr.onload = function () {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        if (response.success_url) {
          window.location.href = response.success_url;
        } else if (response.error) {
          alert("Upload error: " + response.error);
          progressContainer.style.display = "none";
        }
      } else {
        alert("Upload failed. Please try again.");
        progressContainer.style.display = "none";
      }
    };

    xhr.onerror = function () {
      alert("Upload error. Please check your connection.");
      progressContainer.style.display = "none";
    };

    xhr.open("POST", "/", true);
    xhr.send(formData);
  });
});
