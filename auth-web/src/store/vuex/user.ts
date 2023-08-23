import { Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { User } from '@/models/user'
import store from '.'
import { useUserStore } from '../user'

// Remove with Vue3 - Note this needs to persist until we change sbc-common-components to not call this function.
@Module({
  name: 'user',
  namespaced: true,
  store: store,
  dynamic: true
})
export class UserModule extends VuexModule {
  // Note this needs to persist until we change sbc-common-components to not call this function.
  @Mutation
  public setUserProfile (userProfile: User | undefined) {
    // TODO: TEST THIS!!
    const userStore = useUserStore()
    userStore.setUserProfile(userProfile)
  }
}
