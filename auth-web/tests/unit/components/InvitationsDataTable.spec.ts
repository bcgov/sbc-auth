import { createLocalVue, shallowMount } from '@vue/test-utils'
import BusinessModule from '@/store/modules/business'
import InvitationsDataTable from '@/components/auth/InvitationsDataTable.vue'
import UserService from '../../../src/services/user.services'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)

describe('InvitationsDataTable.vue', () => {
  let localVue
  let store

  const config = {
    VUE_APP_ROOT_API: 'https://localhost:8080/api/v1/11',
    VUE_APP_COPS_REDIRECT_URL: 'https://coops-dev.pathfinder.gov.bc.ca/',
    VUE_APP_PAY_ROOT_API: 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)
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

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('Shows empty panel message', () => {
    UserService.getOrganizations = jest.fn().mockResolvedValue({ orgs: [] })
    const $t = () => ''
    const wrapper = shallowMount(InvitationsDataTable, {
      store,
      localVue,
      mocks: { $t }
    })
    expect(wrapper.text()).toContain('')
  })
})
