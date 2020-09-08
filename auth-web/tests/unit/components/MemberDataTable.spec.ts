import { Wrapper, createLocalVue, mount, shallowMount } from '@vue/test-utils'
import MemberDataTable from '@/components/auth/MemberDataTable.vue'
import OrgModule from '@/store/modules/org'
import UserModule from '@/store/modules/user'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)

jest.mock('../../../src/services/bcol.services')

describe('MemberDataTable.vue', () => {
  let localVue
  let store
  let wrapper: any

  const config = {
    VUE_APP_ROOT_API: 'https://localhost:8080/api/v1/11',
    VUE_APP_COPS_REDIRECT_URL: 'https://coops-dev.pathfinder.gov.bc.ca/',
    VUE_APP_PAY_ROOT_API: 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Vuex)
    const orgModule = {
      namespaced: true,
      state: {
        pendingOrgInvitations: [],
        currentOrganization: {},
        activeOrgMembers: [{
          'id': 2909,
          'membershipStatus': 'ACTIVE',
          'membershipTypeCode': 'USER',
          'user': {
            'contacts': [
              {
                'created': '2020-02-12T21:45:01.285260+00:00',
                'createdBy': 'BCREGTEST Delbert TWENTYFIVE',
                'email': 'foo@bar.com',
                'links': [
                  128
                ],
                'modified': '2020-02-12T21:45:01.285278+00:00',
                'phone': '',
                'phoneExtension': '',
                'versions': []
              }
            ],
            'firstname': 'BCREGTEST Delbert',
            'id': 20,
            'lastname': 'TWENTYFIVE',
            'loginSource': 'BCSC',
            'modified': '2020-08-25T20:43:13.232326+00:00',
            'username': 'bcsc/malpaovmqyxtxfdu47z54mwswuerbdni'
          }
        },
        {
          'id': 2906,
          'membershipStatus': 'ACTIVE',
          'membershipTypeCode': 'COORDINATOR',
          'user': {
            'contacts': [
              {
                'created': '2019-11-28T20:05:54.449895+00:00',
                'createdBy': 'BCREGTEST Bashshar TWENTYTWO',
                'email': 'test@gmail.com',
                'links': [
                  12
                ],
                'modified': '2019-12-18T20:54:01.894819+00:00',
                'modifiedBy': 'BCREGTEST Bashshar TWENTYTWO',
                'phone': '',
                'phoneExtension': '57',
                'versions': []
              }
            ],
            'firstname': 'BCREGTEST Bashshar',
            'id': 6,
            'lastname': 'TWENTYTWO',
            'loginSource': 'BCSC',
            'modified': '2020-07-24T22:02:20.312360+00:00',
            'username': 'bcsc/c272kovlg2knludndfrstiklgufitypx'
          }
        },
        {
          'id': 141,
          'membershipStatus': 'ACTIVE',
          'membershipTypeCode': 'ADMIN',
          'user': {
            'contacts': [
              {
                'created': '2020-05-14T21:12:20.058359+00:00',
                'createdBy': 'BCREGTEST Bena THIRTEEN',
                'email': 'test@test.com',
                'links': [
                  714
                ],
                'modified': '2020-07-17T18:04:29.006705+00:00',
                'modifiedBy': 'BCREGTEST Bena THIRTEEN',
                'phone': '(778) 678-9998',
                'phoneExtension': '123',
                'versions': []
              }
            ],
            'firstname': 'BCREGTEST Bena',
            'id': 4,
            'lastname': 'THIRTEEN',
            'loginSource': 'BCSC',
            'modified': '2020-09-08T17:51:29.648717+00:00',
            'username': 'bcsc/fyd76wbcng76cpxbu42hhua4qphtivb5'
          }
        }],
        pendingOrgMembers: [{ 'membershipTypeCode': 'OWNER', 'user': { 'username': 'test' } }]
      },
      actions: {
        createInvitation: jest.fn(),
        resendInvitation: jest.fn()
      },
      mutations: {
        resetInvitations: jest.fn()
      },
      getters: OrgModule.getters
    }
    const userModule = {
      namespaced: true,
      state: {
        currentUser: { 'userName': 'test' }
      },
      actions: {
        getRoleInfo: jest.fn()
      }
    }
    const businessModule = {
      namespaced: true,
      state: {
        businesses: []
      }
    }

    store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule,
        user: userModule,
        business: businessModule
      }
    })

    const $t = () => 'test'
    wrapper = shallowMount(MemberDataTable, {
      store,
      localVue,
      mocks: { $t }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('Mounting works', () => {
    expect(wrapper.find('.v-data-table')).toBeTruthy()
    expect(wrapper.find('.user-name')).toBeTruthy()
  })

  it('Data verification', () => {
    expect(wrapper.find('.user-name')[0]).toEqual('BCREGTEST Delbert TWENTYFIVE')
  })
})
