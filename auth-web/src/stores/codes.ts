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
    businessSizeCodes: [] as Code[],
    businessTypeCodes: [] as Code[],
    onholdReasonCodes: [] as Code[],
    suspensionReasonCodes: [] as Code[]
  })

  function $reset () {
    state.businessSizeCodes = []
    state.businessTypeCodes = []
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

  async function getBusinessTypeCodes (): Promise<Code[]> {
    const response = await CodesService.getCodes(this.businessTypeCodeTable)
    if (response?.data && response.status === 200) {
      const result = response.data.sort((a, b) => a.desc.localeCompare(b.desc))
      state.businessTypeCodes = result
      return result
    }
    state.businessTypeCodes = []
    return []
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
    getBusinessSizeCodes,
    getBusinessTypeCodes,
    getCodes,
    getOnholdReasonCodes,
    onholdReasonCodeTable,
    suspensionReasonCodeTable,
    $reset
  }
})
