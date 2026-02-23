/**
 * Audio Extractor – frontend: submit URL to backend (same as main.py).
 */

(function () {
  "use strict";

  const linkInput = document.getElementById("link-input");
  const fileInput = document.getElementById("file-input");
  const downloadConfirm = document.getElementById("download-confirm");
  const confirmText = downloadConfirm && downloadConfirm.querySelector(".download-confirm__text");
  const inputError = document.getElementById("input-error");

  if (!linkInput || !downloadConfirm) return;

  function setConfirm(text, state) {
    if (!confirmText) return;
    confirmText.textContent = text;
    downloadConfirm.className = "download-confirm download-confirm--" + (state || "default");
    if (inputError) {
      inputError.hidden = true;
      inputError.textContent = "";
    }
  }

  function setError(message) {
    if (inputError) {
      inputError.textContent = message;
      inputError.hidden = false;
    }
    setConfirm("Download ready", "default");
  }

  function setLoading(loading) {
    linkInput.disabled = loading;
    if (fileInput) fileInput.disabled = loading;
    if (loading) setConfirm("Extracting…", "default");
  }

  linkInput.addEventListener("keydown", function (e) {
    if (e.key !== "Enter") return;
    e.preventDefault();
    const url = linkInput.value.trim();
    if (!url) {
      setError("Please enter a link.");
      return;
    }

    setLoading(true);
    if (inputError) inputError.hidden = true;

    fetch("/api/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url }),
    })
      .then(function (res) {
        return res.json().then(function (data) {
          if (res.ok && data.success) {
            const filename = data.output_path ? data.output_path.split(/[/\\]/).pop() : "audio";
            setConfirm("Saved: " + filename, "default");
            linkInput.value = "";
          } else {
            setError(data.error_message || "Extraction failed.");
          }
        });
      })
      .catch(function () {
        setError("Network error. Try again.");
      })
      .finally(function () {
        setLoading(false);
      });
  });

  if (fileInput) {
    fileInput.addEventListener("change", function () {
      const file = fileInput.files && fileInput.files[0];
      if (!file) return;

      setLoading(true);
      if (inputError) inputError.hidden = true;

      const form = new FormData();
      form.append("file", file);

      fetch("/api/extract-file", {
        method: "POST",
        body: form,
      })
        .then(function (res) {
          return res.json().then(function (data) {
            if (res.ok && data.success) {
              const filename = data.output_path ? data.output_path.split(/[/\\]/).pop() : "audio";
              setConfirm("Saved: " + filename, "default");
            } else {
              setError(data.error_message || "Extraction failed.");
            }
          });
        })
        .catch(function () {
          setError("Network error. Try again.");
        })
        .finally(function () {
          setLoading(false);
          fileInput.value = "";
        });
    });
  }
})();
