import { createLocalVue, shallowMount } from '@vue/test-utils'
import Statements from '@/components/auth/account-settings/statement/Statements.vue'
import UserService from '../../../src/services/user.services'

import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(VueI18n)
Vue.use(VueRouter)
Vue.use(Vuetify)

describe('Statements.vue', () => {
  let localVue
  let store

  const config = {
    VUE_APP_ROOT_API: 'https://localhost:8080/api/v1/app',
    VUE_APP_COPS_REDIRECT_URL: 'https://test.gov.bc.ca/',
    VUE_APP_PAY_ROOT_API: 'https://pay-api.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Vuex)
    const orgModule = {
      namespaced: true,
      actions: {
        getStatementsList: jest.fn(),
        getStatement: jest.fn(),
        getTransactionList: jest.fn(() => {
          return [
            {
              'id': 9656,
              'transactionNames': [
                'Priority Request fee'
              ],
              'folioNumber': '',
              'businessIdentifier': '',
              'initiatedBy': 'BCREGTEST Bena TEST',
              'transactionDate': '2021-05-10T21:49:21.412338+00:00',
              'totalAmount': '101.50',
              'status': 'PAD Invoice Approved',
              'details': [
                {
                  'label': 'NR Number:',
                  'value': 'NR1234567'
                },
                {
                  'label': 'Name Choices:',
                  'value': ''
                },
                {
                  'label': '1.',
                  'value': 'CINEXTREME LEGAL SERVICES LIMITED'
                },
                {
                  'label': '2.',
                  'value': 'BRUNETTE HUNTING AND TRAPPING LIMITED'
                },
                {
                  'label': '3.',
                  'value': 'ALKEM CLOTHING STORES LIMITED'
                }
              ]
            }]
        })
      },
      state: {
        currentOrganization: {
          'accessType': 'REGULAR',
          'billable': true,
          'created': '2021-05-02T20:54:15.936923+00:00',
          'createdBy': 'BCREGTEST Bena TEST',
          'hasApiAccess': false,
          'id': 2663,
          'loginOptions': [],
          'modified': '2021-05-02T20:54:15.936935+00:00',
          'name': 'NEW BC ONLINE TECH TEAM - DEV1',
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
          'bcolAccountDetails': { }
        },
        currentMembership: {
          'id': 3458,
          'membershipStatus': 'ACTIVE',
          'membershipTypeCode': 'ADMIN',
          'user': {
            'contacts': [
              {
                'created': '2021-04-30T20:54:17.109390+00:00',
                'createdBy': 'BCREGTEST Bena TEST',
                'email': 'test1@test.com',
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
        }
      }
    }
    store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule
      }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('Shows empty panel message', () => {
    UserService.getOrganizations = jest.fn().mockResolvedValue({ orgs: [] })
    const $t = () => ''
    const wrapper = shallowMount(Statements, {
      store,
      localVue,
      mocks: { $t }
    })
    expect(wrapper.text()).toContain('')
  })
})
