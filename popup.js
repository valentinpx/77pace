document.addEventListener('alpine:init', () => {
  Alpine.data('timeData', () => ({
      months: {},
      async init() { this.months = (await chrome.storage.local.get(['months'])).months || {} }
  }))
  Alpine.data('totalData', () => ({
      total: {},
      async init() { this.total = (await chrome.storage.local.get(['total'])).total || {} }
  }))
})
