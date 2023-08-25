import '@/composition-api-setup'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import AccountDeactivate from '@/views/auth/AccountDeactivate.vue'
import DeactivateCard from '@/components/auth/account-deactivate/DeactivateCard.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import i18n from '@/plugins/i18n'

const router = new VueRouter()
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccountDeactivate.vue', () => {
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()

    wrapper = shallowMount(AccountDeactivate, {
      localVue,
      i18n,
      router,
      vuetify
    })
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('AccountDeactivate is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })
  it('AccountDeactivate contains the card', () => {
    expect(wrapper.findComponent(DeactivateCard).exists()).toBe(true)
  })
})
