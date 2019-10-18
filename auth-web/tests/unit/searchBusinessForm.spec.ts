import { createLocalVue, mount } from '@vue/test-utils'
import BusinessModule from '@/store/modules/business'
import SearchBusinessForm from '@/components/auth/SearchBusinessForm.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import VuexPersistence from 'vuex-persist'

Vue.use(Vuetify)
Vue.use(VueRouter)

jest.mock('axios', () => ({
  post: jest.fn(() => Promise.resolve({ data: { access_token: 'abcd', refresh_token: 'efgh', registries_trace_id: '12345abcde' } }))
}))

describe('SearchBusinessForm.vue', () => {
  let cmp
  var ob = {
    'VUE_APP_COPS_REDIRECT_URL': 'http://localhost:8081',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_AUTH_ROOT_API': 'https://auth-api-post-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_LEGAL_ROOT_API': 'https://legal-api-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_FLAVOR': 'post-mvp'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(ob)
  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const vuexPersist = new VuexPersistence({
      key: 'AUTH_WEB',
      storage: sessionStorage
    })

    const store = new Vuex.Store({
      strict: false,
      modules: {
        business: BusinessModule
      },
      plugins: [vuexPersist.plugin]
    })

    const $t = () => {}

    let vuetify = new Vuetify({})

    cmp = mount(SearchBusinessForm, {
      store,
      localVue,
      vuetify,
      mocks: { $t }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('searchbusiness screen enter button exists', () => {
    expect(cmp.find('.search-btn').text().startsWith('Enter')).toBeTruthy()
    expect(cmp.isVueInstance()).toBeTruthy()
  })

  it('incorporation number is empty', () => {
    expect(cmp.vm.businessNumber).toBe('')
  })

  it('enter button click invokes searchBusiness method', () => {
    const stub = jest.fn()
    cmp.setMethods({ searchBusiness: stub })
    cmp.find('.search-btn').trigger('click')
    expect(cmp.vm.searchBusiness).toBeCalled()
  })

  it('enter button click invokes isFormValid method', () => {
    const stub = jest.fn()
    cmp.setMethods({ isFormValid: stub })
    cmp.find('.search-btn').trigger('click')
    expect(cmp.vm.isFormValid).toBeCalled()
  })
})
