import { Code, PaymentMethod } from '@/models/Code'
import { reactive, toRefs } from '@vue/composition-api'
import CodesService from '@/services/codes.service'
import { defineStore } from 'pinia'

export const useCodesStore = defineStore('codes', () => {
  const businessSizeCodeTable = 'business_size_codes'
  const businessTypeCodeTable = 'business_type_codes'
  const onholdReasonCodeTable = 'staff_remark_codes'
  const suspensionReasonCodeTable = 'suspension_reason_codes'

  const state = reactive({
    allBusinessTypeCodes: [] as Code[],
    businessSizeCodes: [] as Code[],
    businessTypeCodes: [] as Code[],
    governmentTypeCodes: [] as Code[],
    onholdReasonCodes: [] as Code[],
    suspensionReasonCodes: [] as Code[],
    productPaymentMethods: {} as {[key: string]: Array<string>},
    paymentMethods: [] as PaymentMethod[]
  })

  function $reset () {
    state.allBusinessTypeCodes = []
    state.businessSizeCodes = []
    state.businessTypeCodes = []
    state.governmentTypeCodes = []
    state.onholdReasonCodes = []
    state.suspensionReasonCodes = []
    state.productPaymentMethods = {}
    state.paymentMethods = []
  }

  async function getBusinessSizeCodes (): Promise<Code[]> {
    const response = await CodesService.getCodes(this.businessSizeCodeTable)
    if (response?.data && response.status === 200) {
      state.businessSizeCodes = response.data
      return response.data
    }
    state.businessSizeCodes = []
    return []
  }

  async function fetchAllBusinessTypeCodes (): Promise<void> {
    const response = await CodesService.getCodes(this.businessTypeCodeTable)
    if (response?.data && response.status === 200) {
      state.allBusinessTypeCodes = response.data
    } else {
      state.allBusinessTypeCodes = []
    }
  }

  function getBusinessTypeCodes (): Code[] {
    const filteredCodes = state.allBusinessTypeCodes.filter(code => code.isBusiness)
    state.businessTypeCodes = filteredCodes.sort((a, b) => a.desc.localeCompare(b.desc))
    return state.businessTypeCodes
  }

  function getGovernmentTypeCodes (): Code[] {
    const filteredCodes = state.allBusinessTypeCodes.filter(code => code.isGovernmentAgency)
    state.governmentTypeCodes = filteredCodes.sort((a, b) => a.desc.localeCompare(b.desc))
    return state.governmentTypeCodes
  }

  async function getCodes (): Promise<Code[]> {
    const response = await CodesService.getCodes(this.suspensionReasonCodeTable)
    if (response?.data && response.status === 200) {
      state.suspensionReasonCodes = response.data
      return response.data
    }
  }

  async function getOnholdReasonCodes (): Promise<Code[]> {
    const response = await CodesService.getCodes(this.onholdReasonCodeTable)
    if (response?.data && response.status === 200) {
      state.onholdReasonCodes = response.data
      return response.data
    }
  }

  async function getProductPaymentMethods (productCode?: string): Promise<any> {
    const data = await CodesService.getProductPaymentMethods(productCode)
    data.BUSINESS_SEARCH = data?.BUSINESSSearch // Force to match enum.
    state.productPaymentMethods = data
  }

  async function getPaymentMethods (): Promise<void> {
    state.paymentMethods = await CodesService.getPaymentMethodCodes()
  }

  return {
    ...toRefs(state),
    businessSizeCodeTable,
    businessTypeCodeTable,
    fetchAllBusinessTypeCodes,
    getBusinessSizeCodes,
    getBusinessTypeCodes,
    getCodes,
    getGovernmentTypeCodes,
    getOnholdReasonCodes,
    onholdReasonCodeTable,
    suspensionReasonCodeTable,
    getProductPaymentMethods,
    getPaymentMethods,
    $reset
  }
})
