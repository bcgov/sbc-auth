import { createLocalVue, mount } from '@vue/test-utils'
import BusinessModule from '@/store/modules/business'
import SearchBusinessView from '@/views/auth/staff/SearchBusinessView.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

jest.mock('axios', () => ({
  post: jest.fn(() => Promise.resolve({ data: { access_token: 'abcd', refresh_token: 'efgh', registries_trace_id: '12345abcde' } }))
}))

describe('SearchBusinessView.vue', () => {
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

    const businessModule = {
      namespaced: true,
      state: {
        currentBusiness: {
          businessIdentifier: 'CP0000000',
          businessNumber: 'CP0000000',
          contacts: [
            {
              created: '2019-12-11T04:03:11.830365+00:00',
              createdBy: 'TEST',
              email: 'test@gmail.com',
              modified: '2019-12-11T04:03:11.830395+00:00',
              phone: '',
              phoneExtension: ''
            }
          ],
          folioNumber: '22222222222'
        }
      }
    }

    const userModule = {
      namespaced: true,
      state: {
        currentUser: { 'userName': 'test' }
      }
    }

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        business: businessModule,
        user: userModule
      }
    })

    const $t = () => {}

    let vuetify = new Vuetify({})

    cmp = mount(SearchBusinessView, {
      store,
      localVue,
      vuetify,
      mocks: { $t }
    })
    cmp.setData({ businessNumber: 'CP0000000' })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('searchbusiness screen enter button exists', () => {
    expect(cmp.find('.search-btn').text().startsWith('Search')).toBeTruthy()
    expect(cmp.isVueInstance()).toBeTruthy()
  })

  it('incorporation number is empty', () => {
    expect(cmp.vm.businessNumber).toBe('CP0000000')
  })

  it('enter button click invokes searchBusiness method', () => {
    const stub = jest.fn()
    cmp.setMethods({ search: stub })
    cmp.find('.search-btn').trigger('click')
    expect(cmp.vm.search).toBeCalled()
  })

  it('enter button click invokes isFormValid method', () => {
    const stub = jest.fn()
    cmp.setMethods({ isFormValid: stub })
    cmp.find('.search-btn').trigger('click')
    expect(cmp.vm.isFormValid).toBeCalled()
  })
})
