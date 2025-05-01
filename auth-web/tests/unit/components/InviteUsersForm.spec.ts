import { AccessType, Role } from '@/util/constants'
import { createLocalVue, mount, shallowMount } from '@vue/test-utils'
import { useOrgStore, useUserStore } from '@/stores'
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

  it('availableRoles getter filters out admin role for non-admin members', async () => {
    const $t = () => 'test'

    const userStore = useUserStore()
    userStore.roleInfos = [
      {
        'default': false,
        'desc': 'Admin for the organization',
        'displayName': 'Admin',
        'icon': 'mdi-shield-account',
        'label': 'Manage team members and account settings',
        'name': 'ADMIN'
      },
      {
        'default': false,
        'desc': 'Member of the organization',
        'displayName': 'Team Member',
        'icon': 'mdi-account',
        'label': 'Submit searches and filings',
        'name': 'USER'
      }
    ] as any

    orgStore.currentMembership = [{
      membershipTypeCode: 'USER',
      membershipStatus: 'ACTIVE',
      user: { username: 'test' }
    }] as any

    wrapper = mount(InviteUsersForm, {
      localVue,
      mocks: { $t },
      stubs: {
        'v-overflow-btn': `<div/>`
      }
    })

    await Vue.nextTick()

    expect(wrapper.vm.availableRoles.length).toBe(1)
    expect(wrapper.vm.availableRoles[0].name).toBe('USER')
  })

  it('availableRoles includes admin role for staff with StaffManageAccounts role', async () => {
    const $t = () => 'test'

    const userStore = useUserStore()
    userStore.currentUser = {
      userName: 'test',
      roles: ['staff', Role.StaffManageAccounts]
    } as any

    userStore.roleInfos = [
      {
        'default': false,
        'desc': 'Admin for the organization',
        'displayName': 'Admin',
        'icon': 'mdi-shield-account',
        'label': 'Manage team members and account settings',
        'name': 'ADMIN'
      },
      {
        'default': false,
        'desc': 'Member of the organization',
        'displayName': 'Team Member',
        'icon': 'mdi-account',
        'label': 'Submit searches and filings',
        'name': 'USER'
      }
    ] as any

    orgStore.currentMembership = [{
      membershipTypeCode: 'USER',
      membershipStatus: 'ACTIVE',
      user: { username: 'test' }
    }] as any

    wrapper = mount(InviteUsersForm, {
      localVue,
      mocks: { $t },
      stubs: {
        'v-overflow-btn': `<div/>`
      }
    })

    await Vue.nextTick()

    // Staff with StaffManageAccounts role should have access to admin role despite not being an admin member
    expect(wrapper.vm.availableRoles.length).toBe(2)
    expect(wrapper.vm.availableRoles.some(role => role.name === 'ADMIN')).toBeTruthy()
  })
})
