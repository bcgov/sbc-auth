import { createLocalVue, shallowMount } from '@vue/test-utils'
import AccountHoldView from '@/views/auth/account-freeze/AccountHoldView.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'
import { useOrgStore } from '@/stores/org'

const mockSession = {
  'NRO_URL': 'Mock NRO URL',
  'NAME_REQUEST_URL': 'Mock Name Request URL'
}

const router = new VueRouter()
const vuetify = new Vuetify({})

describe('AccountHoldView.vue', () => {
  let wrapper: any

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  beforeEach(() => {
    const orgStore = useOrgStore()
    orgStore.currentOrganization = {
      name: 'testOrg',
      suspendedOn: 'January 12, 2021'
    }
    sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const localVue = createLocalVue()
    wrapper = shallowMount(AccountHoldView, {
      localVue,
      router,
      vuetify,
      mocks: {
        $t: (mock) => mock
      },
      propsData: {
        isAdmin: false
      },
      data () {
        return {
          accountAdministratorEmail: 'test@email.com'
        }
      }
    })
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('Validate is-user message', () => {
    expect(wrapper.find('h1').text()).toBe('Your Account is Temporarily on Hold')
    expect(wrapper.find('[data-test="div-is-user"]').text()).toBe('Your account is suspended from: 2021-01-11 ' +
    'Please contact the account administrator to reactive your account.  ' +
    'Account Administrator Email: test@email.com')
    expect(wrapper.find('[data-test="div-is-admin"]').exists()).toBeFalsy()
  })

  it('Validate is-admin message', async () => {
    wrapper.setProps({ isAdmin: true })
    await flushPromises()
    expect(wrapper.find('h1').text()).toBe('Your Account is Temporarily on Hold')
    const divAdminText = wrapper.find('[data-test="div-is-admin"]').text()
    expect(divAdminText).toContain('Your account is on hold until payment is received. ' +
    'Once your payment is processed, your account will be activated. ' +
    'We will send a notification email when your account is activated.')
    expect(wrapper.find('[data-test="div-is-user"]').exists()).toBeFalsy()
  })
})
