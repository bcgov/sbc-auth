import { Ref, ref } from '@vue/composition-api'
import { useOrgStore } from '@/store/org'

export const useAccountChangeHandler = () => {
  const unregisterHandler: Ref<() => void> = ref(null)
  const setAccountChangedHandler = (handler: () => any) => {
    unregisterHandler.value = useOrgStore().$onAction(({ name, after }) => {
      after(() => {
        if (name === 'setCurrentOrganization') {
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
