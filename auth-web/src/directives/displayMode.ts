import { DirectiveBinding } from 'vue/types/options'
import { DirectiveOptions } from 'vue'
import { DisplayModeValues } from '@/util/constants'
import { useOrgStore } from '@/store/org'

interface CustomHTMLElement extends HTMLElement {
  disabled: boolean
  readOnly: boolean
}

const displayMode: DirectiveOptions = {
  inserted (el, binding) {
    checkViewOnlyMode(binding, el)
  },
  componentUpdated (el, binding) {
    checkViewOnlyMode(binding, el)
  }
}

/**
 *
 * @param binding
 * @param el
 * How to use
 * v-display-mode only with out any value, this will check the value from org store and disable/enable div
 * v-display-mode="'VIEW_ONLY'", when pass value to thsi directive it will check the value and disable/enable div
 */
function checkViewOnlyMode (binding: DirectiveBinding, el: HTMLElement) {
  const directiveValue = binding.value

  const vModeStoreValue:string = useOrgStore().vDisplayModeValue
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
