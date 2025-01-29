const DAY_LENGTH = 7
const PRECISION = 2
const DELAY = 1000


function timeToJ(time) {
  let splitted = time.split(":")

  return Number(((Number(splitted[0])
    + Number(splitted[1]) / 60
    + Number(splitted[2]) / 3600)
    / DAY_LENGTH)
    .toFixed(PRECISION))
}

function formatDate(month) {
  const [m, y] = month.split(", ")
  const months = { "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12 }
  
  return `${y}-${months[m]}`
}

function storeMonth(month, time, days) {
  if (isNaN(time)) return

  chrome.storage.local.get(['months'], function(result) {
    let months = result.months || {}
    months[formatDate(month)] = { name: month, time, days }
    
    chrome.storage.local.set({ months: months })
  })
}

function computeDays() {
  const month = document.querySelector(".month-total.day-hours")

  console.log("77pace days loading")
  if (month) {
    let days = {
      hours: 0,
      min: 0,
      sec: 0,
      length: 0
    }
    let monthJ = timeToJ(month.innerText)

    for (const day of document.querySelectorAll(".selectable-day:not(.not-current-month) .day-hours")) {
        let time = day.innerText

        if (/^([0-9]+:[0-9]+:[0-9]+)$/.test(time)) {
          days.length += 1
          day.innerHTML += `<p>${timeToJ(time)}j</p>`
        }
    }
    if (days.length === 0) {
      setTimeout(computeDays, DELAY)
    }
    if (isNaN(monthJ)) return
    month.innerHTML += `<p>${monthJ}j/${days.length}<p>`
    console.log("77pace days loaded")

    storeMonth(
      document.querySelector(".month-selector .ttt-selector-area").innerText,
      monthJ,
      days.length
    )
  } else {
    setTimeout(computeDays, DELAY)
  }
}

for (const btn of [...document.querySelectorAll(".ttt-month-switcher"), document.querySelector(".ttt-current-period-btn")]) {
  btn.addEventListener("click", computeDays)
}
computeDays()