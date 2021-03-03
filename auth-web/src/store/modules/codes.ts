import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'

import { Code } from '@/models/Code'
import CodesService from '@/services/codes.service'

@Module({ namespaced: true })
export default class CodesModule extends VuexModule {
    suspensionReasonCodes: Code[] = []
    private suspensionReasonCodeTable: string = 'suspension_reason_codes'

    @Mutation
    public setSuspensionReasonCodes (codes: Code[]) {
      this.suspensionReasonCodes = codes
    }

    @Action({ commit: 'setSuspensionReasonCodes', rawError: true })
    public async getCodes (): Promise<Code[]> {
      const response = await CodesService.getCodes(this.suspensionReasonCodeTable)
      if (response && response.data && response.status === 200) {
        return response.data
      }
    }
}
