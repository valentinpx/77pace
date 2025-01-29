document.addEventListener('alpine:init', () => {
  Alpine.data('timeData', () => ({
      months: {},
      async init() { this.months = (await chrome.storage.local.get(['months'])).months || {} }
  }))
})
