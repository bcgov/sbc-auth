import '../test-utils/composition-api-setup' // important to import this first
import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import DashboardView from '@/views/auth/DashboardView.vue'

import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

vi.mock('../../../src/plugins/i18n', () => {})

Vue.use(Vuetify)
Vue.use(VueRouter)
const router = new VueRouter()

describe('DashboardView.vue', () => {
  let wrapper: Wrapper<DashboardView>
  const ob = {
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
    'AUTH_API_URL': 'https://auth-api-post-dev.pathfinder.gov.bc.ca/api/v1',
    'LEGAL_API_URL': 'https://legal-api-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_FLAVOR': 'post-mvp'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(ob)
  beforeEach(() => {
    const localVue = createLocalVue()

    wrapper = mount(DashboardView, {
      localVue,
      router,
      stubs: {
        ManagementMenu: true,
        TeamManagement: true,
        EntityManagement: true
      }
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })
})
