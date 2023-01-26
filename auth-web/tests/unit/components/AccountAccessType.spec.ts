import { AccessType, Account, AccountStatus } from '@/util/constants'
import { createLocalVue, mount } from '@vue/test-utils'

import AccountAccessType from '@/components/auth/account-settings/account-info/AccountAccessType.vue'
import { Organization } from '@/models/Organization'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import can from '@/directives/can'

Vue.use(Vuetify)
Vue.use(VueRouter)

document.body.setAttribute('data-app', 'true')

describe('AccountAccessType.vue', () => {
  let wrapper: any
  const localVue = createLocalVue()
  localVue.directive('can', can)
  const vuetify = new Vuetify({})
  const organization: Organization = {
    name: 'testOrg',
    statusCode: AccountStatus.ACTIVE,
    accessType: AccessType.REGULAR,
    id: 1,
    orgType: Account.PREMIUM
  }

  beforeEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    const $t = () => ''
    wrapper = mount(AccountAccessType, {
      localVue,
      vuetify,
      propsData: {
        organization: organization,
        viewOnlyMode: true,
        canChangeAccessType: true
      },
      mocks: { $t
      }
    })
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('validate view mode with regular org', () => {
    const $t = () => ''
    wrapper = mount(AccountAccessType, {
      localVue,
      vuetify,
      propsData: {
        organization: organization,
        viewOnlyMode: true,
        canChangeAccessType: true
      },
      mocks: { $t
      }
    })

    expect(wrapper.find('[data-test="title"]').text()).toBe('Access Type')
    expect(wrapper.find('[data-test="txt-selected-access-type"]').text()).toBe('Regular Access')
    expect(wrapper.find('[data-test="btn-edit"]').exists()).toBeTruthy()
  })

  it('accesstype actions', () => {
    const $t = () => ''
    wrapper = mount(AccountAccessType, {
      localVue,
      vuetify,
      propsData: {
        organization: organization,
        viewOnlyMode: false,
        canChangeAccessType: true
      },
      mocks: { $t
      }
    })

    expect(wrapper.vm.currentOrgPaymentTypePad).toBeFalsy()
  })

  it('validate view mode with govn org', () => {
    const $t = () => ''
    const govnOrg = organization
    govnOrg.accessType = AccessType.GOVN
    wrapper = mount(AccountAccessType, {
      localVue,
      vuetify,
      propsData: {
        organization: govnOrg,
        viewOnlyMode: true,
        canChangeAccessType: true
      },
      mocks: { $t
      }
    })

    expect(wrapper.find('[data-test="title"]').text()).toBe('Access Type')
    expect(wrapper.find('[data-test="txt-selected-access-type"]').text()).toBe('Government agency (other than BC provincial)')
    expect(wrapper.find('[data-test="btn-edit"]').exists()).toBeFalsy()
  })

  it('validate view mode with govm org', () => {
    const $t = () => ''
    const govmOrg = organization
    govmOrg.accessType = AccessType.GOVM
    wrapper = mount(AccountAccessType, {
      localVue,
      vuetify,
      propsData: {
        organization: govmOrg,
        viewOnlyMode: true,
        canChangeAccessType: true
      },
      mocks: { $t
      }
    })

    expect(wrapper.find('[data-test="title"]').text()).toBe('Access Type')
    expect(wrapper.find('[data-test="txt-selected-access-type"]').text()).toBe('BC Government Ministry')
    expect(wrapper.find('[data-test="btn-edit"]').exists()).toBeFalsy()
  })
})
