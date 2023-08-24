import { Ref, ref } from '@vue/composition-api'
import { useOrgStore } from '@/store/org'

export const useAccountChangeHandler = () => {
  const unregisterHandler: Ref<() => void> = ref(null)
  const setAccountChangedHandler = (handler: () => any) => {
    unregisterHandler.value = useOrgStore().$onAction(({ name, after }) => {
      after(() => {
        if (['syncOrganization', 'setCurrentOrganization'].includes(name)) {
          handler()
        }
      })
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
