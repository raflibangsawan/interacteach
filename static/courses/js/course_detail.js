document.addEventListener("DOMContentLoaded", () => {
  // Module toggle functionality
  const moduleHeaders = document.querySelectorAll(".module-header")

  moduleHeaders.forEach((header) => {
    header.addEventListener("click", function () {
      const moduleContent = this.nextElementSibling
      const moduleToggle = this.querySelector(".module-toggle")

      // Close all other modules
      document.querySelectorAll(".module-content").forEach((content) => {
        if (content !== moduleContent && content.style.display === "block") {
          content.style.display = "none"
          content.previousElementSibling.querySelector(".module-toggle").textContent = "+"
          content.previousElementSibling.querySelector(".module-toggle").style.transform = "rotate(0deg)"
        }
      })

      // Toggle current module
      if (moduleContent.style.display === "block") {
        moduleContent.style.display = "none"
        moduleToggle.textContent = "+"
        moduleToggle.style.transform = "rotate(0deg)"
      } else {
        moduleContent.style.display = "block"
        moduleToggle.textContent = "−"
        moduleToggle.style.transform = "rotate(180deg)"
      }
    })
  })

  // Open the first module by default
  const firstModule = document.querySelector(".module-card")
  if (firstModule) {
    const moduleHeader = firstModule.querySelector(".module-header")
    if (moduleHeader) {
      moduleHeader.click()
    }
  }

  // Add smooth animation to progress bar
  const progressFill = document.querySelector(".progress-fill")
  if (progressFill) {
    const width = progressFill.style.width
    progressFill.style.width = "0"

    setTimeout(() => {
      progressFill.style.width = width
    }, 300)
  }
})

