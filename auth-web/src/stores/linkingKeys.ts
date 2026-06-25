import {
  AccountLinkingKey,
  AccountLinkingKeysResponse,
  LinkingKeyActionDetails
} from '@/models/vendorConnection'
import LinkingKeysService from '@/services/linkingKeys.services'
import { defineStore } from 'pinia'

// Note: defined outside store to avoid SonarQube S7721 (nested async functions)
async function fetchLinkingKeys (orgId: number): Promise<AccountLinkingKeysResponse> {
  const response = await LinkingKeysService.getOrgLinkingKeys(orgId)
  return response?.data || { linkingKeys: [] }
}

async function revokeLinkingKey (linkingKeyDetails: LinkingKeyActionDetails): Promise<Record<string, never>> {
  const response = await LinkingKeysService.revokeOrgLinkingKey(linkingKeyDetails)
  return response?.data || {}
}

async function extendLinkingKey (linkingKeyDetails: LinkingKeyActionDetails): Promise<AccountLinkingKey | Record<string, never>> {
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
