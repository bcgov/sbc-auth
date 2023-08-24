import { createLocalVue, mount } from '@vue/test-utils'
import SetupGovmAccountForm from '@/components/auth/staff/SetupGovmAccountForm.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})
const router = new VueRouter()

const mockSession = {
  'NRO_URL': 'Mock NRO URL',
  'NAME_REQUEST_URL': 'Mock Name Request URL'
}

describe('SetupGovmAccountForm.vue', () => {
  let wrapper: any
  const localVue = createLocalVue()

  beforeEach(() => {
    sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
  })

  it('Should have h4 title', () => {
    wrapper = mount(SetupGovmAccountForm, {
      vuetify,
      localVue,
      router,
      mocks: {
        $t: (mock) => mock
      }
    })

    expect(wrapper.vm).toBeTruthy()
    expect(wrapper.find('h4').text()).toBe('Enter Ministry Information for this account')
    wrapper.destroy()
  })
})
