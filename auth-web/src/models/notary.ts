import { Address, IAddress } from '@/models/address'

export interface NotaryInformation {
    notaryName?: string
    address?: IAddress
    key?: string
}

export interface NotaryContact {
    email?: string
    phone?: string
    extension?: string
    key?: string
}
