import { DirectiveBinding } from 'vue/types/options'
import { DirectiveOptions } from 'vue'
import { VNode } from 'vue/types'
import store from '@/store'

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
  const behaviour = binding.modifiers.disable ? 'disable' : 'hide'
  const requestedAction = binding.arg
  const permissions:string[] = (store.state as any)?.org?.permissions
  const customeEl = el as CustomHTMLElement
  const okayToAccess = permissions.indexOf(requestedAction) >= 0
  // if not okay , hide or disable
  if (!okayToAccess) {
    if (behaviour === 'hide') {
      commentNode(el, node)
    } else if (behaviour === 'disable') {
      customeEl.disabled = true
    } else if (behaviour === 'readonly') {
      customeEl.readOnly = true
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
    // @ts-ignore
    vnode.componentInstance.$el = comment
  }

  if (el.parentNode) {
    el.parentNode.replaceChild(comment, el)
  }
}
export default can
