import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'

import { Code } from '@/models/code'
import CodesService from '@/services/codes.service'

@Module({
  name: 'codes',
  namespaced: true
})
export default class CodesModule extends VuexModule {
    suspensionReasonCodeForActiveAccount: Code = undefined
    suspensionReasonCodes: Code[] = []
    test: string = 'test'
    private readonly suspensionReasonCodeTable: string = 'suspension_reason_code'

    @Mutation
    public setSuspensionReasonCodeForActiveAccount (code: Code) {
      this.suspensionReasonCodeForActiveAccount = code
    }

    @Mutation
    public setSuspensionReasonCodes (codes: Code[]) {
      this.suspensionReasonCodes = codes
    }

    @Action({ commit: 'setSuspensionReasonCodes', rawError: true })
    public async syncSuspensionReasonCodes (): Promise<Code[]> {
      const response = await CodesService.getSuspensionReasonCodes(this.suspensionReasonCodeTable)
      if (response && response.data && response.status === 200) {
        return response.data
      }
    }
}
