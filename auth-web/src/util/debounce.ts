export function debounce<F extends (...params: any[]) => void>(fn: F, delay = 300) {
  let timeoutID: number = null
  return function (this: any, ...args: any[]) {
    clearTimeout(timeoutID)
    timeoutID = window.setTimeout(() => fn.apply(this, args), delay)
  } as F
}

export default debounce
