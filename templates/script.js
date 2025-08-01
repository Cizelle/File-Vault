const form = document.getElementById("uploadForm");
const progressBar = document.getElementById("progressBar");
const progressContainer = document.getElementById("progressContainer");
const progressText = document.getElementById("progressText");

form.onsubmit = function (e) {
  e.preventDefault();
  const xhr = new XMLHttpRequest();
  const formData = new FormData(form);

  progressContainer.style.display = "block";

  xhr.upload.addEventListener("progress", function (event) {
    if (event.lengthComputable) {
      let percent = Math.round((event.loaded / event.total) * 100);
      progressBar.style.width = percent + "%";
      progressText.textContent = percent + "% uploaded";
    }
  });

  xhr.onload = function () {
    window.location.href = "/" + xhr.responseURL.split("/").pop();
  };
  xhr.open("POST", "/", true);
  xhr.send(formData);
};
