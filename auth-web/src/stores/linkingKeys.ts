import { reactive, toRefs } from '@vue/composition-api'
import { AccountLinkingKey } from '@/models/vendorConnection'
import LinkingKeysService from '@/services/linkingKeys.services'
import { defineStore } from 'pinia'

async function revokeLinkingKey (linkingKeyDetails) {
  const response = await LinkingKeysService.revokeOrgLinkingKey(linkingKeyDetails)
  return response?.data || {}
}

async function extendLinkingKey (linkingKeyDetails) {
  const response = await LinkingKeysService.extendOrgLinkingKey(linkingKeyDetails)
  return response?.data || {}
}

export const useLinkingKeysStore = defineStore('linkingKeys', () => {
  const state = reactive({
    linkingKeys: [] as AccountLinkingKey[],
    isLoading: false
  })

  async function fetchLinkingKeys (orgId: number) {
    state.isLoading = true
    try {
      const response = await LinkingKeysService.getOrgLinkingKeys(orgId)
      state.linkingKeys = response?.data?.linkingKeys || []
      return response?.data || {}
    } finally {
      state.isLoading = false
    }
  }

  function $reset () {
    state.linkingKeys = []
    state.isLoading = false
  }

  return {
    ...toRefs(state),
    fetchLinkingKeys,
    revokeLinkingKey,
    extendLinkingKey,
    $reset
  }
})
