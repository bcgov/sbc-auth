import ConfigHelper from 'sbc-common-components/src/util/config-helper'
import { DirectiveBinding } from 'vue/types/options'
import { DirectiveOptions } from 'vue'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { VNode } from 'vue/types'
import { useOrgStore } from '@/store/org'

interface CustomHTMLElement extends HTMLElement {
  disabled: boolean
  readOnly: boolean
}

const can: DirectiveOptions = {
  inserted (el, binding, node) {
    canAccess(binding, el, node)
  },
  componentUpdated (el, binding, node) {
    canAccess(binding, el, node)
  }
}

function canAccess (binding: DirectiveBinding, el: HTMLElement, node: VNode) {
  // do not block account creation .
  // check if there is any account in session , if not , do not block any permissions
  const accountId = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount) || '{}').id || 0
  if (!accountId) {
    return
  }
  const behaviour = binding.modifiers.disable ? 'disable' : 'hide'
  // to handle special elements like v-card etc
  const isCard = !!binding.modifiers.card
  const requestedAction = binding.arg
  const permissions:string[] = useOrgStore().permissions
  const customeEl = el as CustomHTMLElement
  const okayToAccess = permissions.indexOf(requestedAction) >= 0
  // if not okay , hide or disable
  if (!okayToAccess) {
    if (behaviour === 'hide') {
      commentNode(el, node)
    } else if (behaviour === 'disable' && isCard === false) {
      customeEl.disabled = true
    } else if (behaviour === 'disable' && isCard === true) {
      // TODO tab still works.. can tab to the text field and make it work
      customeEl.classList.add('v-card--disabled')
      customeEl.style.pointerEvents = 'none'
    }
  }
}

/**
 * Create comment node
 *
 * @private
 * @author https://stackoverflow.com/questions/43003976/a-custom-directive-similar-to-v-if-in-vuejs#43543814
 */
function commentNode (el: HTMLElement, vnode: VNode) {
  const comment = document.createComment(' ')

  Object.defineProperty(comment, 'setAttribute', {
    value: () => undefined
  })

  vnode.text = ' '
  vnode.elm = comment
  vnode.isComment = true
  vnode.tag = undefined

  vnode.data = vnode.data || {}
  vnode.data.directives = undefined

  if (vnode.componentInstance) {
    /* eslint-disable-next-line @typescript-eslint/ban-ts-comment */
    // @ts-ignore
    vnode.componentInstance.$el = comment
  }

  if (el.parentNode) {
    el.parentNode.replaceChild(comment, el)
  }
}
export default can
