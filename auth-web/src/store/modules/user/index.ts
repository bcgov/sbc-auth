import { Module, VuexModule, Mutation, Action } from 'vuex-module-decorators'
import keycloakService from '@/services/keycloak.services'
import userServices from '@/services/user.services'
import { UserInfo } from '@/models/userInfo'

@Module({
  name: 'user'
})
export default class UserModule extends VuexModule {
<<<<<<< HEAD
  
=======
>>>>>>> 0bf492981fada7e1c895140dcebe2ebae034db34
  currentUser: UserInfo

  userProfile: any

  @Mutation
  public setUserProfile (userProfile: any) {
    this.userProfile = userProfile
  }

<<<<<<< HEAD
  @Mutation
  public setCurrentUser (currentUser: UserInfo) {
    this.currentUser = currentUser
  }

=======
>>>>>>> 0bf492981fada7e1c895140dcebe2ebae034db34
  @Action({ rawError: true })
  public async initKeycloak (idpHint:string) {
    return keycloakService.init(idpHint)
  }

<<<<<<< HEAD
  @Action({ commit: 'setCurrentUser' })
=======
  @Action({ rawError: true })
>>>>>>> 0bf492981fada7e1c895140dcebe2ebae034db34
  public async initializeSession () {
    // Set values to session storage
    keycloakService.initSessionStorage()
    // Load User Info
<<<<<<< HEAD
    return keycloakService.getUserInfo()
=======
    this.currentUser = keycloakService.getUserInfo()
>>>>>>> 0bf492981fada7e1c895140dcebe2ebae034db34
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
<<<<<<< HEAD
  
  @Action({ commit: 'setUserProfile' })
  public async createUserProfile () {
    return userServices.createUserProfile()
      .then(response => {
        return response.data
      })
  }
=======
>>>>>>> 0bf492981fada7e1c895140dcebe2ebae034db34
}
