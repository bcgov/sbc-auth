import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import Signin from '@/views/auth/SigninView.vue'
import Vuetify from 'vuetify'

describe('Signin.vue', () => {
  let wrapper: Wrapper<Signin>
  const keyCloakConfig = {
    'AUTH_API_URL': 'https://auth-api-post-dev.pathfinder.gov.bc.ca/api/v1',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
    'VUE_APP_FLAVOR': 'post-mvp'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(keyCloakConfig)

  beforeEach(() => {
    const localVue = createLocalVue()
    const vuetify = new Vuetify({})

    wrapper = shallowMount(Signin, {
      vuetify,
      localVue
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })
})
