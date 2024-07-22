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
    month.innerHTML += `<p>${timeToJ(month.innerText)}j/${days.length}<p>`
    console.log("77pace days loaded")
  } else {
    setTimeout(computeDays, DELAY)
  }
}


for (const btn of [...document.querySelectorAll(".ttt-month-switcher"), document.querySelector(".ttt-current-period-btn")]) {
  btn.addEventListener("click", computeDays)
}
computeDays()