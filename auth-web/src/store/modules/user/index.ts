import { Module, VuexModule, Mutation, Action } from 'vuex-module-decorators'
import keycloakService from '@/services/keycloak.services'
import userServices from '@/services/user.services'
import { UserInfo } from '@/models/userInfo'

@Module({
  name: 'user'
})
export default class UserModule extends VuexModule {
  
  currentUser: UserInfo

  userProfile: any 
  
  @Mutation
  public setUserProfile (userProfile: any) {
    this.userProfile = userProfile
  }

  @Action({ rawError: true })
  public async initKeycloak () {
    return keycloakService.init()
  }

  @Action({ rawError: true })
  public async initializeSession () {
    //Set values to session storage
    keycloakService.initSessionStorage()
    //Load User Info
    this.currentUser = keycloakService.getUserInfo()
  }

  @Action({ rawError: true })
  public login (idpHint:string) {
    keycloakService.login(idpHint)
  }

  @Action({ rawError: true })
  public async getUserProfile (keycloakGuid: string) {
    return userServices.getUserProfile(keycloakGuid)
      .then(response => {
        console.log(response.status)
        if ((response.status === 200 || response.status === 201) && response.data) {
          this.context.commit('setUserProfile', response.data)
        }
      }).catch(error => {
        console.error('Error in get user profile', error)
        this.context.commit('setUserProfile', null)
      })
  }

}
