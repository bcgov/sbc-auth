import { Ref, ref } from '@vue/composition-api'
import { useStore } from 'vuex-composition-helpers'

export const useAccountChangeHandler = () => {
  const unregisterHandler: Ref<() => void> = ref(null)
  const setAccountChangedHandler = (handler: () => any) => {
    const store = useStore()
    unregisterHandler.value = store.subscribe((mutation) => {
      if (mutation.type === 'org/setCurrentOrganization') {
        handler()
      }
    })
  }
  const beforeDestroy = () => {
    unregisterHandler.value && unregisterHandler.value()
  }

  return {
    setAccountChangedHandler,
    beforeDestroy
  }
}
