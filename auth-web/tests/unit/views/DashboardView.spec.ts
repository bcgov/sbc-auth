import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import BusinessContactForm from '@/components/auth/BusinessContactForm.vue'
import BusinessModule from '@/store/modules/business'
import DashboardView from '@/views/auth/DashboardView.vue'
import SupportInfoCard from '@/components/SupportInfoCard.vue'

import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
const router = new VueRouter()

describe('DashboardView.vue', () => {
  let wrapper: Wrapper<DashboardView>
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
      },
      getters: {
        myOrgMembership: jest.fn()
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
        UserManagement: true,
        EntityManagement: true
      }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })
})
