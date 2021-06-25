import { DirectiveBinding } from 'vue/types/options'
import { DirectiveOptions } from 'vue'
import { DisplayModeValues } from '@/util/constants'
import { VNode } from 'vue/types'
import store from '@/store'

interface CustomHTMLElement extends HTMLElement {
  disabled: boolean
  readOnly: boolean
}

const displayMode: DirectiveOptions = {
  inserted (el, binding, node) {
    checkViewOnlyMode(binding, el, node)
  },
  componentUpdated (el, binding, node) {
    checkViewOnlyMode(binding, el, node)
  }
}

/**
 *
 * @param binding
 * @param el
 * @param node
 * How to use
 * v-display-mode only with out any value, this will check the value from org store and disable/enable div
 * v-display-mode="'VIEW_ONLY'", when pass value to thsi directive it will check the value and disable/enable div
 */
function checkViewOnlyMode (binding: DirectiveBinding, el: HTMLElement, node: VNode) {
  const directiveValue = binding.value

  const vModeStoreValue:string = (store.state as any)?.org?.vDisplayModeValue
  const customeEl = el as CustomHTMLElement
  let viewOnly = false
  if (directiveValue) {
    viewOnly = directiveValue === DisplayModeValues.VIEW_ONLY
  } else {
    viewOnly = vModeStoreValue === DisplayModeValues.VIEW_ONLY
  }
  // if viewOnly, disable div
  if (viewOnly) {
    // Add disable class to element
    customeEl.classList.add('v-card--disabled')
    customeEl.style.pointerEvents = 'none'
  }
}

export default displayMode
