import { createLocalVue, shallowMount } from '@vue/test-utils'
import { AccountStatus } from '@/util/constants'
import AccountTypeSelector from '@/components/auth/create-account/AccountTypeSelector.vue'
import Vuetify from 'vuetify'
import can from '@/directives/can'
import { useOrgStore } from '@/store/org'

document.body.setAttribute('data-app', 'true')

describe('AccountTypeSelector.vue', () => {
  let wrapper: any
  let store: any
  const localVue = createLocalVue()
  localVue.directive('can', can)
  const vuetify = new Vuetify({})

  const config = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11',
    'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const orgStore = useOrgStore()
    orgStore.currentOrganization = {
      name: 'testOrg',
      statusCode: AccountStatus.ACTIVE,
      orgStatus: AccountStatus.ACTIVE
    }
    orgStore.isCurrentSelectedProductsPremiumOnly = true
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    wrapper = shallowMount(AccountTypeSelector, {
      localVue,
      vuetify,
      stubs: {
        'ConfirmCancelButton': {
          template: `<div></div>`
        }
      },
      propsData: {
        isAccountChange: false
      }
    })
    expect(wrapper.vm).toBeTruthy()
  })

  it('disables basic type when premium products are selected', () => {
    wrapper = shallowMount(AccountTypeSelector, {
      localVue,
      vuetify,
      stubs: {
        'ConfirmCancelButton': {
          template: `<div></div>`
        }
      },
      propsData: {
        isAccountChange: false
      }
    })
    const orgStore = useOrgStore()
    orgStore.isCurrentSelectedProductsPremiumOnly = true
    expect(wrapper.find("[data-test='div-stepper-basic']").attributes('disabled')).toBeTruthy()
    expect(wrapper.find("[data-test='div-stepper-premium']").attributes('disabled')).toBeFalsy()
    expect(wrapper.find("[data-test='badge-account-premium']").exists()).toBeTruthy()
  })

  it('enables basic type when non premium products are selected', async () => {
    wrapper = shallowMount(AccountTypeSelector, {
      store,
      localVue,
      vuetify,
      stubs: {
        'ConfirmCancelButton': {
          template: `<div></div>`
        }
      },
      propsData: {
        isAccountChange: false
      }
    })
    const orgStore = useOrgStore()
    orgStore.isCurrentSelectedProductsPremiumOnly = false
    await wrapper.vm.$nextTick()
    expect(wrapper.find("[data-test='div-stepper-basic']").attributes('disabled')).toBeFalsy()
    expect(wrapper.find("[data-test='div-stepper-premium']").attributes('disabled')).toBeFalsy()
    expect(wrapper.find("[data-test='badge-account-premium']").exists()).toBeFalsy()
  })

  it('Should set selectedAccountType as PREMIUM', () => {
    wrapper = shallowMount(AccountTypeSelector, {
      localVue,
      vuetify,
      stubs: {
        'ConfirmCancelButton': {
          template: `<div></div>`
        }
      },
      propsData: {
        isAccountChange: false
      }
    })
    const orgStore = useOrgStore()
    orgStore.currentOrganization = {
      name: 'testOrg2',
      statusCode: AccountStatus.ACTIVE,
      orgStatus: AccountStatus.ACTIVE,
      orgType: 'PREMIUM'
    }
    expect(wrapper.vm.selectedAccountType).toEqual('PREMIUM')
  })
})
