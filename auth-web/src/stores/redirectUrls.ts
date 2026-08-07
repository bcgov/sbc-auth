import { OrgRedirectUrl, OrgRedirectUrls } from '@/models/Organization'
import { EmptyResponse } from '@/models/global'
import OrgService from '@/services/org.services'
import { defineStore } from 'pinia'

// Note: defined outside store to avoid SonarQube S7721 (nested async functions)
async function getOrgRedirectUrls (orgId: number): Promise<OrgRedirectUrls> {
  const response = await OrgService.getOrgRedirectUrls(orgId)
  return response?.data || { redirectUrls: [] }
}

async function createOrgRedirectUrl (details: { orgId: number, redirectUrl: string }):
Promise<OrgRedirectUrl | Record<string, never>> {
  const { orgId, redirectUrl } = details
  const response = await OrgService.createOrgRedirectUrl(orgId, { redirectUrl })
  return response?.data || {}
}

async function updateOrgRedirectUrl (details: { orgId: number, urlId: number, redirectUrl: string }):
Promise<OrgRedirectUrl | Record<string, never>> {
  const { orgId, urlId, redirectUrl } = details
  const response = await OrgService.updateOrgRedirectUrl(orgId, urlId, { redirectUrl })
  return response?.data || {}
}

async function deleteOrgRedirectUrl (details: { orgId: number, urlId: number }): Promise<EmptyResponse> {
  const { orgId, urlId } = details
  const response = await OrgService.deleteOrgRedirectUrl(orgId, urlId)
  return response?.data || {}
}

function $reset () {
  // placeholder for resetting the store (on logout all stores are reset)
}

export const useRedirectUrlsStore = defineStore('redirectUrls', () => {
  return {
    getOrgRedirectUrls,
    createOrgRedirectUrl,
    updateOrgRedirectUrl,
    deleteOrgRedirectUrl,
    $reset
  }
})
