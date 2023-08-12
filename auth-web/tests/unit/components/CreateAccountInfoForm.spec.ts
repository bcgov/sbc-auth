import { createLocalVue, shallowMount } from '@vue/test-utils'
import CreateAccountInfoForm from '@/components/auth/create-account/CreateAccountInfoForm.vue'
import OrgModule from '@/store/modules/org'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)

vi.mock('../../../src/services/bcol.services')

describe('CreateAccountInfoForm.vue', () => {
  let localVue
  let store

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/11',
    PAY_API_URL: 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Vuex)
    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
        },
        organizations: [],
        orgCreateMessage: 'test'
      },
      actions: {
        createOrg: vi.fn(),
        syncOrganizations: vi.fn()
      },
      mutations: {
        setOrgCreateMessage: vi.fn()
      },
      getters: OrgModule.getters
    }

    store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule
      }
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  it('Mounting works', () => {
    const $t = () => 'test'
    const wrapper = shallowMount(CreateAccountInfoForm, {
      store,
      localVue,
      mocks: { $t }
    })
    expect(wrapper.find('.user-list')).toBeTruthy()
    wrapper.destroy()
  })
})
