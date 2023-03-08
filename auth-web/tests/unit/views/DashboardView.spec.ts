import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import BusinessContactForm from '@/components/auth/BusinessContactForm.vue'
import BusinessModule from '@/store/modules/business'
import DashboardView from '@/views/auth/DashboardView.vue'
import SupportInfoCard from '@/components/SupportInfoCard.vue'

import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

jest.mock('../../../src/plugins/i18n', () => {})

Vue.use(Vuetify)
Vue.use(VueRouter)
const router = new VueRouter()

describe('DashboardView.vue', () => {
  let wrapper: Wrapper<DashboardView>
  var ob = {
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
    'AUTH_API_URL': 'https://auth-api-post-dev.pathfinder.gov.bc.ca/api/v1',
    'LEGAL_API_URL': 'https://legal-api-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_FLAVOR': 'post-mvp'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(ob)
  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const userModule = {
      namespaced: true,
      state: {
        userProfile: {
        }
      },
      actions: {
        getUserProfile: jest.fn()
      }
    }
    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
        }
      },
      actions: {
        syncOrganizations: jest.fn(),
        syncCurrentOrganization: jest.fn()
      }
    }

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        user: userModule,
        org: orgModule
      }
    })

    wrapper = mount(DashboardView, {
      store,
      localVue,
      router,
      stubs: {
        ManagementMenu: true,
        TeamManagement: true,
        EntityManagement: true
      }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper).toBeTruthy()
  })
})
