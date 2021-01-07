import { createLocalVue, mount } from '@vue/test-utils'
import { Account } from '@/util/constants'
import OrgModule from '@/store/modules/org'
import PaymentMethods from '@/components/auth/common/PADInfoForm.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('PADInfoForm.vue', () => {
  let wrapper: any
  const config = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11',
    'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const vuetify = new Vuetify({})

    const userModule = {
      namespaced: true,
      state: {
        userHasToAcceptTOS: false,
      },
      actions: {
        getTermsOfUse: jest.fn()
      },
      mutations: {},
      getters: {}
    }
    const orgModule = {
      namespaced: true,
      state: {
        currentOrgPADInfo: { "bankAccountNumber": "XXX4567", "bankInstitutionNumber": "0001", "bankTransitNumber": "00720", "cfsAccountNumber": "4566", "cfsPartyNumber": "99034", "cfsSiteNumber": "30579", "status": "ACTIVE" },
        currentOrganizationType: Account.BASIC
      },
      actions: OrgModule.actions,
      mutations: OrgModule.mutations,
      getters: OrgModule.getters
    }

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule,
        user: userModule
      }
    })

    wrapper = mount(PaymentMethods, {
      store,
      localVue,
      vuetify,
      propsData: {
        currentOrgType: Account.BASIC
      }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })
})
