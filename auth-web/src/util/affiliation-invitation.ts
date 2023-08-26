import { AffiliationInvitationStatus, AffiliationInviteInfo } from '@/models/affiliation'

export const getFirstPendingAffiliationWithSmallestId = (affiliationInviteInfos: AffiliationInviteInfo[]): AffiliationInviteInfo | undefined => {
  return affiliationInviteInfos?.reduce(
    (currentMin, curr) => (currentMin.id <= curr.id) ? currentMin : curr,
    affiliationInviteInfos.length > 0 ? affiliationInviteInfos[0] : undefined
  )
}
