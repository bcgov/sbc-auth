import { createLocalVue, mount } from '@vue/test-utils'

import AccountFreezeUnlockView from '@/views/auth/account-freeze/AccountFreezeUnlockView.vue'
import { AccountStatus } from '@/util/constants'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import { useOrgStore } from '@/stores'

Vue.use(Vuetify)
Vue.use(VueRouter)
const router = new VueRouter()
const vuetify = new Vuetify({})

const mockSession = {
  'NRO_URL': 'Mock NRO URL',
  'NAME_REQUEST_URL': 'Mock Name Request URL'
}

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccountFreezeUnlockView.vue', () => {
  let wrapper: any

  beforeEach(() => {
    sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const localVue = createLocalVue()
    const orgStore = useOrgStore()
    orgStore.currentOrganization = {
      statusCode: AccountStatus.NSF_SUSPENDED
    } as any
    orgStore.calculateFailedInvoices = vi.fn(() => {
      return {
        totalTransactionAmount: 10,
        totalAmountToPay: 20
      }
    }) as any

    wrapper = mount(AccountFreezeUnlockView, {
      localVue,
      router,
      vuetify,
      mocks: {
        $t: (mock) => mock
      },
      computed: {
        isAccountStatusNsfSuspended: Boolean
      }
    })
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('should render page title', () => {
    expect(wrapper.find('h1').text()).toBe('This account has been temporarily suspended')
  })

  it('should render page title icon', () => {
    expect(wrapper.find('.view-header__icon').find('.v-icon').exists()).toBe(true)
  })

  it('should render stepper', () => {
    expect(wrapper.find('stepper')).toBeTruthy()
  })

  it('should have error dialog', () => {
    expect(wrapper.find({ ref: 'errorDialog' })).toBeTruthy()
  })
})
