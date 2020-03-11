export interface ProductCode {
    code: string
    default: boolean
    desc: string
}

export interface AccountType {
    code: string
    default: boolean
    desc: string
}

export interface ProductsRequestBody {
    subscriptions: Products[],
}

export interface Products {
    productCode: string,
    productRoles: string[]
}
