import { createLocalVue, mount } from '@vue/test-utils'
import AccountOverview from '@/components/auth/account-freeze/AccountOverview.vue'
import OrgModule from '@/store/modules/org'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('AccountOverview.vue', () => {
  let wrapper: any
  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const vuetify = new Vuetify({})

    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {}
      },
      actions: OrgModule.actions,
      mutations: OrgModule.mutations,
      getters: OrgModule.getters
    }

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule
      }
    })

    wrapper = mount(AccountOverview, {
      store,
      localVue,
      vuetify,
      mixins: [Steppable]
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterAll(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('should render info card', () => {
    expect(wrapper.find('.suspended-info-card')).toBeTruthy()
  })

  it('should render download button', () => {
    expect(wrapper.find('.download-pdf-btn')).toBeTruthy()
  })

  it('should render next button', () => {
    expect(wrapper.find('.v-btn').text('Next')).toBeTruthy()
  })
})
