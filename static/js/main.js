document.addEventListener("DOMContentLoaded", () => {
    // Mobile menu toggle
    const menuToggle = document.querySelector(".mobile-menu-toggle")
    const nav = document.querySelector(".nav")
  
    if (menuToggle && nav) {
      menuToggle.addEventListener("click", () => {
        nav.classList.toggle("active")
  
        // Toggle menu icon
        const spans = menuToggle.querySelectorAll("span")
        if (nav.classList.contains("active")) {
          spans[0].style.transform = "rotate(45deg) translate(5px, 5px)"
          spans[1].style.opacity = "0"
          spans[2].style.transform = "rotate(-45deg) translate(7px, -7px)"
        } else {
          spans[0].style.transform = "none"
          spans[1].style.opacity = "1"
          spans[2].style.transform = "none"
        }
      })
    }
  
    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll(".message")
    if (messages.length > 0) {
      setTimeout(() => {
        messages.forEach((message) => {
          message.style.opacity = "0"
          message.style.transition = "opacity 0.5s ease"
  
          setTimeout(() => {
            message.style.display = "none"
          }, 500)
        })
      }, 5000)
    }
  
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", function (e) {
        const href = this.getAttribute("href")
  
        if (href !== "#") {
          e.preventDefault()
  
          const targetElement = document.querySelector(href)
          if (targetElement) {
            targetElement.scrollIntoView({
              behavior: "smooth",
            })
          }
        }
      })
    })
  
    // Add animation to course cards
    const courseCards = document.querySelectorAll(".course-card")
    if (courseCards.length > 0) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.style.opacity = "1"
              entry.target.style.transform = "translateY(0)"
            }
          })
        },
        { threshold: 0.1 },
      )
  
      courseCards.forEach((card) => {
        card.style.opacity = "0"
        card.style.transform = "translateY(20px)"
        card.style.transition = "opacity 0.5s ease, transform 0.5s ease"
        observer.observe(card)
      })
    }
  })
  
  