import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'

import { Code } from '@/models/Code'
import CodesService from '@/services/codes.service'

@Module({ namespaced: true })
export default class CodesModule extends VuexModule {
    suspensionReasonCodes: Code[] = []
    businessSizeCodes: Code[] = []
    businessTypeCodes: Code[] = []
    rejectReasonCodes: Code[] = []

    private suspensionReasonCodeTable = 'suspension_reason_codes'
    private businessSizeCodeTable = 'business_size_codes'
    private businessTypeCodeTable = 'business_type_codes'
    private rejectReasonCodeTable = 'reject_reason_codes'

    @Mutation
    public setSuspensionReasonCodes (codes: Code[]) {
      this.suspensionReasonCodes = codes
    }

    @Mutation
    public setBusinessSizeCodes (codes: Code[]) {
      this.businessSizeCodes = codes
    }

    @Mutation
    public setBusinessTypeCodes (codes: Code[]) {
      this.businessTypeCodes = codes
    }

    @Mutation
    public setRejectReasonCodes (codes: Code[]) {
      this.rejectReasonCodes = codes
    }

    @Action({ commit: 'setBusinessSizeCodes', rawError: true })
    public async getBusinessSizeCodes (): Promise<Code[]> {
      const response = await CodesService.getCodes(this.businessSizeCodeTable)
      if (response && response.data && response.status === 200) {
        return response.data
      }
      return []
    }

    @Action({ commit: 'setBusinessTypeCodes', rawError: true })
    public async getBusinessTypeCodes (): Promise<Code[]> {
      const response = await CodesService.getCodes(this.businessTypeCodeTable)
      if (response && response.data && response.status === 200) {
        return response.data.sort((a, b) => a.desc.localeCompare(b.desc))
      }
      return []
    }

    @Action({ commit: 'setSuspensionReasonCodes', rawError: true })
    public async getCodes (): Promise<Code[]> {
      const response = await CodesService.getCodes(this.suspensionReasonCodeTable)
      if (response && response.data && response.status === 200) {
        return response.data
      }
    }

    @Action({ commit: 'setRejectReasonCodes', rawError: true })
    public async getRejectReasonCodes (): Promise<Code[]> {
      const response = await CodesService.getCodes(this.rejectReasonCodeTable)
      if (response && response.data && response.status === 200) {
        const rejectResons = response.data
        // pushing default reject account value into array since its not included in API
        // TODO make it better approch
        rejectResons.push({
          'code': 'REJECTACCOUNT',
          'default': false,
          'desc': 'Reject Account'
        })
        return rejectResons
      }
    }
}
