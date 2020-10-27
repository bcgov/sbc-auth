import { Address } from '@/models/address'

export interface BcolProfile {
    userId?: string
    password?: string
}
export interface BcolAccountDetails {
    userId?: string
    accountNumber: string
    authCode?: string
    authCodeDesc?: string
    accountType?: string
    accountTypeDesc?: string
    gstStatus?: string
    gstStatusDesc?: string
    pstStatus?: string
    pstStatusDesc?: string
    userName?: string
    orgName?: string
    orgType?: string
    phone?: string
    fax?: string
    profileFlags?:string
    address?:Address
}
