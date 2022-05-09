import { createLocalVue, shallowMount } from '@vue/test-utils'

import { MembershipType } from '@/models/Organization'
import Transactions from '@/components/auth/account-settings/transaction/Transactions.vue'
import UserService from '../../../src/services/user.services'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)

describe('Transactions.vue', () => {
  let localVue
  let store
  let wrapper: any
  let wrapperFactory: any
  const vuetify = new Vuetify({})

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/11',
    PAY_API_URL: 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }
  const router = new VueRouter()
  const $t = () => ''
  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Vuex)

    const orgModule = {
      namespaced: true,
      actions: {
        getTransactionReport: jest.fn()
      },
      state: {
        currentMembership: {
          'id': 3457,
          'membershipStatus': 'ACTIVE',
          'membershipTypeCode': MembershipType.Admin,
          'user': {
            'contacts': [
              {
                'created': '2021-04-30T20:54:17.109390+00:00',
                'createdBy': 'BCREGTEST Bena TEST',
                'email': 'test@test.com',
                'modified': '2021-04-30T20:54:17.109398+00:00',
                'phone': '',
                'phoneExtension': ''
              }
            ],
            'firstname': 'BCREGTEST Bena',
            'id': 4,
            'lastname': 'TEST',
            'loginSource': 'BCSC',
            'modified': '2021-05-11T19:38:35.067210+00:00',
            'username': 'bcsc/fyd76wbcng76cpxbu42hhua4qphtivb5'
          }
        },
        currentOrganization: {
          'accessType': 'REGULAR',
          'bcolAccountId': '126316',
          'bcolAccountName': 'NEW BC ONLINE TECH TEAM',
          'bcolUserId': 'PA32881',
          'created': '2021-04-30T20:54:15.936923+00:00',
          'createdBy': 'BCREGTEST Bena TEST',
          'hasApiAccess': false,
          'id': 2662,
          'loginOptions': [],
          'modified': '2021-04-30T20:54:15.936935+00:00',
          'name': 'NEW BC ONLINE TECH TEAM - DEV',
          'orgType': 'PREMIUM',
          'orgStatus': 'ACTIVE',
          'products': [
            3830,
            3831,
            3832,
            3833,
            3834
          ],
          'statusCode': 'ACTIVE',
          'bcolAccountDetails': {
            'accountNumber': '126316',
            'userId': 'PA32881'
          }
        },
        currentOrgPaymentDetails: {
          credit: 0,
          accountId: 2662
        }
      }
    }
    store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule
      }
    })

    wrapperFactory = (propsData) => {
      return shallowMount(Transactions, {
        store,
        localVue,
        router,
        vuetify,
        mocks: { $t }

      })
    }

    wrapper = wrapperFactory()

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('Shows empty panel message', () => {
    UserService.getOrganizations = jest.fn().mockResolvedValue({ orgs: [] })

    expect(wrapper.text()).toContain('')
  })

  it('renders proper header content', () => {
    expect(wrapper.find('h2').text()).toBe('Transactions')
  })

  it('renders proper header content', () => {
    expect(wrapper.find("[data-test='btn-export-csv']").text()).toBe('Export CSV')
  })
})
