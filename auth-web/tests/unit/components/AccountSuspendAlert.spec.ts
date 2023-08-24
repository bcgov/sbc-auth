import { createLocalVue, shallowMount } from '@vue/test-utils'
import AccountSuspendAlert from '@/components/auth/common/AccountSuspendAlert.vue'
import Vuetify from 'vuetify'
import { useOrgStore } from '@/stores/org'

describe('AccountSuspendAlert.vue', () => {
  let wrapper: any
  beforeEach(() => {
    const localVue = createLocalVue()

    const orgStore = useOrgStore()
    orgStore.calculateFailedInvoices = vi.fn(() => {
      return {
        totalTransactionAmount: 10,
        totalAmountToPay: 20
      }
    }) as any

    const vuetify = new Vuetify({})

    const $t = () => ''
    wrapper = shallowMount(AccountSuspendAlert, {
      localVue,
      vuetify,
      mocks: { $t }
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

  it('Should have Alert', () => {
    expect(wrapper.find('.banner-info')).toBeTruthy()
  })
})
