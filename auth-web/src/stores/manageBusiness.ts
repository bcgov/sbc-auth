import { reactive, toRefs } from '@vue/composition-api'
import { defineStore } from 'pinia'

// This store is specific to the manage business components.
export const useManageBusinessStore = defineStore('manageBusiness', () => {
  const state = reactive({
    businessIdentifier: null
  })

  function setBusinessIdentifier (businessIdentifier: string) {
    state.businessIdentifier = businessIdentifier
  }

  return {
    ...toRefs(state),
    setBusinessIdentifier
  }
})
