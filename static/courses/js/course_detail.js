function toggleModule(moduleId) {
    const moduleContent = document.getElementById(`module-${moduleId}`)
    const moduleToggle = moduleContent.previousElementSibling.querySelector(".module-toggle")
  
    if (moduleContent.style.display === "block") {
      moduleContent.style.display = "none"
      moduleToggle.textContent = "+"
    } else {
      moduleContent.style.display = "block"
      moduleToggle.textContent = "−"
    }
  }
  
  // Open the first module by default
  document.addEventListener("DOMContentLoaded", () => {
    const firstModule = document.querySelector(".module-card")
    if (firstModule) {
      const moduleId = firstModule.querySelector(".module-content").id.replace("module-", "")
      toggleModule(moduleId)
    }
  })
  
  