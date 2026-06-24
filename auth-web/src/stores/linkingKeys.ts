import LinkingKeysService from '@/services/linkingKeys.services'
import { defineStore } from 'pinia'

// Note: defined outside store to avoid SonarQube S7721 (nested async functions)
async function fetchLinkingKeys (orgId: number) {
  const response = await LinkingKeysService.getOrgLinkingKeys(orgId)
  return response?.data || {}
}

async function revokeLinkingKey (linkingKeyDetails) {
  const response = await LinkingKeysService.revokeOrgLinkingKey(linkingKeyDetails)
  return response?.data || {}
}

async function extendLinkingKey (linkingKeyDetails) {
  const response = await LinkingKeysService.extendOrgLinkingKey(linkingKeyDetails)
  return response?.data || {}
}

function $reset () {
  // no-op: store holds no cached state
}

export const useLinkingKeysStore = defineStore('linkingKeys', () => {
  return {
    fetchLinkingKeys,
    revokeLinkingKey,
    extendLinkingKey,
    $reset
  }
})
