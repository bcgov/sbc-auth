import { createLocalVue, mount, shallowMount } from '@vue/test-utils'
import { useOrgStore, useUserStore } from '@/store'
import { AccessType } from '@/util/constants'
import InviteUsersForm from '@/components/auth/account-settings/team-management/InviteUsersForm.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'

vi.mock('../../../src/services/bcol.services')

describe('InviteUsersForm.vue', () => {
  let wrapper: any
  let orgStore: any
  const localVue = createLocalVue()

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/11',
    PAY_API_URL: 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)
  beforeEach(() => {
    localVue.use(Vuetify)

    orgStore = useOrgStore()
    orgStore.pendingOrgInvitations = [{
      id: 1,
      recipientEmail: 'myemail@mytestemail.com',
      sentDate: '2019-12-11T04:03:11.830365+00:00',
      membership: [],
      expiresOn: '2020-12-11T04:03:11.830365+00:00',
      status: 'pending'
    }] as any
    orgStore.currentOrganization = {
      name: 'testOrg_GovM',
      accessType: AccessType.GOVM
    }
    orgStore.currentMembership = [{
      membershipTypeCode: 'OWNER',
      membershipStatus: 'ACTIVE',
      user: { username: 'test' }
    }] as any
    orgStore.setCurrentOrganization = vi.fn().mockImplementation(() => {
      orgStore.currentOrganization = {
        name: 'testOrg_regular',
        accessType: AccessType.REGULAR
      }
    })

    const userStore = useUserStore()
    userStore.currentUser = { userName: 'test' } as any
    userStore.roleInfos = [{
      'default': false,
      'desc': 'Admin for the organization',
      'displayName': 'Account Coordinator',
      'icon': 'mdi-settings',
      'label': 'Submit searches and filings, add / remove businesses, add / remove team members',
      'name': 'COORDINATOR'
    }] as any


    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('Mounting works', () => {
    const $t = () => 'test'
    wrapper = shallowMount(InviteUsersForm, {
      localVue,
      mocks: { $t }
    })
    expect(wrapper.find('.invite-list')).toBeTruthy()
  })

  it('GovM behavior', async () => {
    const $t = () => 'test'

    wrapper = mount(InviteUsersForm, {
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
      localVue,
      mocks: { $t },
      stubs: {
        'v-overflow-btn': `<div/>`
      }
    })
    orgStore.setCurrentOrganization()

    expect(wrapper.vm.isAccountGovM).toBeFalsy()
    wrapper.find("[data-test='email-address-0']").setValue('test1@gmail.com')
    wrapper.find("[data-test='email-address-1']").setValue('test2@gmail.com')
    wrapper.find("[data-test='email-address-2']").setValue('test3@gmail.com')

    await Vue.nextTick()

    expect(wrapper.vm.isFormValid()).toBeTruthy()
  })
})
