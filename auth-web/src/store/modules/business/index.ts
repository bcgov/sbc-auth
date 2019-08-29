import { Module, VuexModule, Mutation, Action } from 'vuex-module-decorators'
import loginServices from '@/services/login.services'
import { Business } from '@/models/business'
import { Contact } from '@/models/contact'
import businessServices from '@/services/business.services'
import { Entity } from '@/models/entity'
import { Org } from '@/models/org'
import Axios, { AxiosPromise, AxiosResponse } from 'axios'

interface LoginPayload {
  businessNumber: string
  passCode: string
}

@Module({
  name: 'business'
})
export default class BusinessModule extends VuexModule {
  currentBusiness: Business = {
    businessIdentifier: ''
  }

  currentOrg: Org = {
    name: ''
  }

  skippedContactEntry = false

  @Mutation
  public setCurrentBusiness (business: Business) {
    this.currentBusiness = business
  }

  @Mutation
  public setSkippedContactEntry (skippedStatus: boolean) {
    this.skippedContactEntry = skippedStatus
  }

  @Action({ rawError: true })
  public async login (payload: LoginPayload) {
    return loginServices.login(payload.businessNumber, payload.passCode)
  }

  @Action
  public async loadBusiness (businessNumber: string) {
    return businessServices.getBusiness(businessNumber)
      .then(response => {
        if (response.data) {
          this.context.commit('setCurrentBusiness', response.data)
        }
      })
      .catch(() => {
        businessServices.createBusiness({ businessIdentifier: businessNumber })
          .then(createResponse => {
            if ((createResponse.status === 200 || createResponse.status === 201) && createResponse.data) {
              this.context.commit('setCurrentBusiness', createResponse.data)
            }
          })
      })
  }

  @Action({ rawError: true })
  public async addBusiness (businessIdentifier: string, passCode: string) { 
    console.log('###########The businessIdentifier is: ' + businessIdentifier)      
    let orgFound: boolean = false
    let orgIdentifier: string = ''

    const entity: Entity = {
      businessIdentifier: businessIdentifier,
      name: '',
      businessNumber: '',
      passCode: passCode
    }
   
    businessServices.getOrgs().then(response => { console.log('########### getOrgs response123: ' + response); }).catch(error => { console.log(' ########### getOrgs response456: ' + error); });
    console.log('###########222The businessIdentifier is: ' + businessIdentifier)    

    // businessServices.createOrg ({ name: businessIdentifier }).then(response => { console.log('########### createOrgresponse123: ' + response.data); }).catch(error => { console.log('########### createOrg response456: ' + error); });     
         
    // businessServices.createAffiliation (orgIdentifier, entity)
    
    //  businessServices.getOrgs()
    //   .then(response => {
    //     if (response.data) {   
    //       console.log('###########The respon response.data is: ' + response.data)  
            
    //       response.data.orgs.forEach(element => {
    //         console.log('###########The element.id is: ' + element.id)    
    //         console.log('###########The element.name is: ' + element.name) 
    //         if (element.name === businessIdentifier) {
    //           orgFound = true
    //           orgIdentifier = element.id
    //         }
    //       })
    //     }
    //   }).catch(function (error) { console.log('########### response: ' + error); });

    //   if (orgFound === false) {
    //     businessServices.createOrg ({ name: businessIdentifier })       
    //       .then(createResponse => {
    //         if ((createResponse.status === 200 || createResponse.status === 201) && createResponse.data) {
    //           for (var id in createResponse.data) {
    //             orgIdentifier = createResponse.data[id]
    //           } 
    //         }
    //       }).catch(function (error) { console.log('########### response: ' + error); });        
    //   } 

    //   businessServices.createAffiliation (orgIdentifier, entity)
    //   .then(createResponse => {
    //     if ((createResponse.status === 200 || createResponse.status === 201) && createResponse.data) {
    //       this.context.commit('setCurrentBusiness', createResponse.data) 
    //     }
    //   }).catch(function (error) { console.log('########### response: ' + error); });      
  }

  @Action({ rawError: true })
  public async addContact (contact: Contact) {
    return businessServices.addContact(this.currentBusiness, contact)
      .then(response => {
        if ((response.status === 200 || response.status === 201) && response.data) {
          this.context.commit('setCurrentBusiness', response.data)
        }
      })
  }

  @Action({ rawError: true })
  public async updateContact (contact: Contact) {
    return businessServices.updateContact(this.currentBusiness, contact)
      .then(response => {
        if ((response.status === 200 || response.status === 201) && response.data) {
          this.context.commit('setCurrentBusiness', response.data)
        }
      })
  }
}
