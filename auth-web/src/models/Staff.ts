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

export interface GLCode {
    client: string,
    createdBy: string,
    createdName: string,
    createdOn: Date,
    distributionCodeId: number,
    endDate: Date,
    memoName: string,
    projectCode: string,
    responsibilityCentre: string,
    serviceFeeClient: number,
    serviceFeeLine: number,
    serviceFeeMemoName: string,
    serviceFeeProjectCode: number,
    serviceFeeResponsibilityCentre: number,
    serviceFeeStob: number,
    serviceLine: number,
    startDate: string,
    stob: string,
    updatedBy: string,
    updatedName: string,
    updatedOn: Date
}

export interface GLCodeResponse {
    items: GLCode[]
}

export interface FilingType {
    corpType: string
    fee: string
    feeEndDate: string
    feeScheduleId: string
    feeStartDate: string
    filingType: string
    futureEffectiveFee: string
    priorityFee: string
    serviceFee: string
}

export interface FilingTypeResponse {
    items: FilingType[]
}
