import { createLocalVue, mount } from '@vue/test-utils'
import InvitationsDataTable from '@/components/auth/account-settings/team-management/InvitationsDataTable.vue'
import UserService from '../../../src/services/user.services'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)
const vuetify = new Vuetify({})

describe('InvitationsDataTable.vue', () => {
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
        pendingOrgInvitations: []
      }
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

  it('Shows empty panel message', () => {
    UserService.getOrganizations = vi.fn().mockResolvedValue({ orgs: [] })
    const $t = () => ''
    const wrapper = mount(InvitationsDataTable, {
      store,
      vuetify,
      localVue,
      mocks: { $t }
    })
    expect(wrapper.text()).toContain('')
    wrapper.destroy()
  })
})
