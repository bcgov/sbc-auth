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

  @Mutation
  public setCurrentUser (currentUser: UserInfo) {
    this.currentUser = currentUser
  }

  @Action({ rawError: true })
  public async initKeycloak (idpHint:string) {
    return keycloakService.init(idpHint)
  }

  @Action({ commit: 'setCurrentUser' })
  public async initializeSession () {
    // Set values to session storage
    keycloakService.initSessionStorage()
    // Load User Info
    return keycloakService.getUserInfo()
    this.currentUser = keycloakService.getUserInfo()
  }

  @Action({ rawError: true })
  public login (idpHint:string) {
    keycloakService.login(idpHint)
  }

  @Action({ commit: 'setUserProfile' })
  public async getUserProfile (identifier: string) {
    return userServices.getUserProfile(identifier)
      .then(response => {
        return response.data ? response.data:null
      }).catch(error => {
        return null
      })
  }
  
  @Action({ commit: 'setUserProfile' })
  public async createUserProfile () {
    return userServices.createUserProfile()
      .then(response => {
        return response.data
      })
  }
}
