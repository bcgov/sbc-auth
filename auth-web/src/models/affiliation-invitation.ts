export interface AffiliationInvitationOrg {
    id: number
    name: string
    orgType: string
}

export interface AffiliationInvitation {
    id: number
    businessIdentifier: string
    expiresOn?: string
    fromOrg?: AffiliationInvitationOrg
    toOrg?: AffiliationInvitationOrg
    receipientEmail?: string
    sentDate?: string
    status: string
    token?: string
    type: string
}

export interface CreateAffiliationInvitation {
    fromOrgId: number
    toOrgId?: string
    businessIdentifier: string
    toOrgUuid?: string
    type?: string
    additionalMessage?: string
}

export interface OrgsDetails {
    name: string
    uuid: string
}
