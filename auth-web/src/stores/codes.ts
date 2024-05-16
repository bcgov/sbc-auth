import { reactive, toRefs } from '@vue/composition-api'
import { Code } from '@/models/Code'
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
    suspensionReasonCodes: [] as Code[]
  })

  function $reset () {
    state.allBusinessTypeCodes = []
    state.businessSizeCodes = []
    state.businessTypeCodes = []
    state.governmentTypeCodes = []
    state.onholdReasonCodes = []
    state.suspensionReasonCodes = []
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
    const response = await CodesService.getCodes(businessTypeCodeTable)
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

  return {
    ...toRefs(state),
    businessSizeCodeTable,
    businessTypeCodeTable,
    fetchAllBusinessTypeCodes,
    getBusinessSizeCodes,
    getBusinessTypeCodes,
    getBusinessTypeCodesDelete,
    getCodes,
    getGovernmentTypeCodes,
    getOnholdReasonCodes,
    onholdReasonCodeTable,
    suspensionReasonCodeTable,
    $reset
  }
})
