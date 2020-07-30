import { Address, BaseAddressModel } from '@/models/address'

export interface NotaryInformation {
    notaryName?: string
    address?: BaseAddressModel
    key?: string
}

export interface NotaryContact {
    email?: string
    phone?: string
    extension?: string
    key?: string
}
