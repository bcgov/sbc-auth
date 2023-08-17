import { createLocalVue, mount, shallowMount } from '@vue/test-utils'

import { AccessType } from '@/util/constants'
import InviteUsersForm from '@/components/auth/account-settings/team-management/InviteUsersForm.vue'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)
document.body.setAttribute('data-app', 'true')

vi.mock('../../../src/services/bcol.services')

describe('InviteUsersForm.vue', () => {
  let store
  let wrapper: any
  const localVue = createLocalVue()

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/11',
    PAY_API_URL: 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)
  beforeEach(() => {
    localVue.use(Vuex)
    localVue.use(Vuetify)

    const orgModule = {
      namespaced: true,
      state: {
        pendingOrgInvitations: [{
          id: 1,
          recipientEmail: 'myemail@mytestemail.com',
          sentDate: '2019-12-11T04:03:11.830365+00:00',
          membership: [],
          expiresOn: '2020-12-11T04:03:11.830365+00:00',
          status: 'pending'
        }],
        currentOrganization: {
          name: 'testOrg_GovM',
          accessType: AccessType.GOVM
        },
        currentMembership: [{
          membershipTypeCode: 'OWNER',
          membershipStatus: 'ACTIVE',
          user: { username: 'test' } }],
        pendingOrgMembers: []
      },
      actions: {
        createInvitation: vi.fn(),
        resendInvitation: vi.fn()
      },
      mutations: {
        resetInvitations: vi.fn(),
        setCurrentOrganization: vi.fn().mockImplementation(() => {
          orgModule.state.currentOrganization = {
            name: 'testOrg_regular',
            accessType: AccessType.REGULAR
          }
        })
      }
    }

    const userModule = {
      namespaced: true,
      state: {
        currentUser: { userName: 'test' },
        roleInfos: [{
          'default': false,
          'desc': 'Admin for the organization',
          'displayName': 'Account Coordinator',
          'icon': 'mdi-settings',
          'label': 'Submit searches and filings, add / remove businesses, add / remove team members',
          'name': 'COORDINATOR'
        }]
      }
    }

    store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule,
        user: userModule
      }
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('Mounting works', () => {
    const $t = () => 'test'
    wrapper = shallowMount(InviteUsersForm, {
      store,
      localVue,
      mocks: { $t }
    })
    expect(wrapper.find('.invite-list')).toBeTruthy()
  })

  it('GovM behavior', async () => {
    const $t = () => 'test'

    wrapper = mount(InviteUsersForm, {
      store,
      localVue,
      mocks: { $t },
      stubs: {
        'v-overflow-btn': `<div/>`
      }
    })

    expect(wrapper.vm.isAccountGovM).toBeTruthy()
    wrapper.find("[data-test='email-address-0']").setValue('test1@gmail.com')
    wrapper.find("[data-test='email-address-1']").setValue('test2@gmail.com')
    wrapper.find("[data-test='email-address-2']").setValue('test3@gmail.com')

    await Vue.nextTick()

    expect(wrapper.vm.isFormValid()).toBeTruthy()

    wrapper.find("[data-test='email-address-0']").setValue('test1@gov.bc.ca')
    wrapper.find("[data-test='email-address-1']").setValue('test2@gov.bc.ca')
    wrapper.find("[data-test='email-address-2']").setValue('test3@gov.bc.ca')

    await Vue.nextTick()

    expect(wrapper.vm.isFormValid()).toBeTruthy()
  })

  it('Regular account behavior', async () => {
    const $t = () => 'test'

    wrapper = mount(InviteUsersForm, {
      store,
      localVue,
      mocks: { $t },
      stubs: {
        'v-overflow-btn': `<div/>`
      }
    })
    store.commit('org/setCurrentOrganization')

    expect(wrapper.vm.isAccountGovM).toBeFalsy()
    wrapper.find("[data-test='email-address-0']").setValue('test1@gmail.com')
    wrapper.find("[data-test='email-address-1']").setValue('test2@gmail.com')
    wrapper.find("[data-test='email-address-2']").setValue('test3@gmail.com')

    await Vue.nextTick()

    expect(wrapper.vm.isFormValid()).toBeTruthy()
  })
})
