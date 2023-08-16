import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'

import { Code } from '@/models/Code'
import CodesService from '@/services/codes.service'

@Module({ namespaced: true })
export default class CodesModule extends VuexModule {
  suspensionReasonCodes: Code[] = []
  businessSizeCodes: Code[] = []
  businessTypeCodes: Code[] = []
  onholdReasonCodes: Code[] = []

  suspensionReasonCodeTable = 'suspension_reason_codes'
  businessSizeCodeTable = 'business_size_codes'
  businessTypeCodeTable = 'business_type_codes'
  onholdReasonCodeTable = 'staff_remark_codes'

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
    public setOnholdReasonCodes (codes: Code[]) {
      this.onholdReasonCodes = codes
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

    @Action({ commit: 'setOnholdReasonCodes', rawError: true })
    public async getOnholdReasonCodes (): Promise<Code[]> {
      const response = await CodesService.getCodes(this.onholdReasonCodeTable)
      if (response && response.data && response.status === 200) {
        return response.data
      }
    }
}
