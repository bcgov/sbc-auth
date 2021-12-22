import { AccessType, AccountStatus, PatchActions } from '@/util/constants'
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
    id: 1
  }

  beforeEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
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

  it('validate view mode', () => {
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
})
