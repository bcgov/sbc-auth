import { Business, BusinessSearchResultDto } from '@/models/business'
import { Wrapper, createLocalVue, mount, shallowMount } from '@vue/test-utils'

import IncorporationSearchResultView from '@/views/auth/staff/IncorporationSearchResultView.vue'
import OrgModule from '@/store/modules/org'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
const router = new VueRouter()
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

const mockSession = {
  'NRO_URL': 'Mock NRO URL',
  'NAME_REQUEST_URL': 'Mock Name Request URL'
}

describe('IncorporationSearchResultView.vue', () => {
  let wrapper: any
  let store: any
  const localVue = createLocalVue()
  localVue.use(Vuex)

  beforeEach(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockSession)

    const affiliatedOrgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
          name: 'test',
          orgType: 'Active',
          accessType: 'Active',
          statusCode: 'Active'
        }
      },
      actions: {
        addOrgSettings: jest.fn()
      }
    }

    const businessModule = {
      namespaced: true,
      state: {
        currentBusiness: {
          name: 'affiliated_test_business',
          businessIdentifier: '123123',
          businessNumber: '1231231'
        }
      }
    }

    store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: affiliatedOrgModule,
        business: businessModule
      }
    })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('Search Result with affiliated CP is valid', () => {
    wrapper = mount(IncorporationSearchResultView, {
      store,
      localVue,
      router,
      vuetify,
      mocks: {
        $t: (mock) => mock
      }
    })

    const searchResult = wrapper.vm.searchResult

    expect(wrapper.isVueInstance()).toBeTruthy()
    expect(searchResult[0].name).toBe('affiliated_test_business')
    expect(searchResult[0].orgType).toBe('Active')
    expect(searchResult[0].account).toBe('test')
    expect(searchResult[0].businessIdentifier).toBe('123123')
    expect(searchResult[0].businessNumber).toBe('1231231')
    expect(searchResult[0].accessType).toBe('Active')
    expect(searchResult[0].statusCode).toBe('Active')
  })

  it('Search Result with unaffiliated CP is valid', () => {
    const unAffiliatedbusinessModule = {
      namespaced: true,
      state: {
        currentBusiness: {
          name: 'unaffiliated_test_business',
          businessIdentifier: '123123',
          businessNumber: '1231231'
        }
      }
    }
    const unAffiliatedOrgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
        }
      },
      actions: {
        addOrgSettings: jest.fn()
      }
    }

    store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: unAffiliatedOrgModule,
        business: unAffiliatedbusinessModule
      }
    })

    wrapper = mount(IncorporationSearchResultView, {
      store,
      localVue,
      router,
      vuetify,
      mocks: {
        $t: (mock) => mock
      }
    })

    const searchResult = wrapper.vm.searchResult

    expect(wrapper.isVueInstance()).toBeTruthy()
    expect(searchResult[0].name).toBe('unaffiliated_test_business')
    expect(searchResult[0].orgType).toBe('N/A')
    expect(searchResult[0].account).toBe('No Affiliation')
    expect(searchResult[0].businessIdentifier).toBe('123123')
    expect(searchResult[0].businessNumber).toBe('1231231')
  })
})
