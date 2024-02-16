import { createLocalVue, shallowMount } from '@vue/test-utils'
import AccountMailingAddress from '@/components/auth/account-settings/account-info/AccountMailingAddress.vue'
import Vuetify from 'vuetify'
import can from '@/directives/can'
import { useCodesStore } from '@/stores'

const vuetify = new Vuetify({})

describe('AccountMailingAddress.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.directive('can', can)

    const codesStore = useCodesStore()
    codesStore.businessSizeCodes = [
      { code: '0-1', default: true, desc: '1 Employee' },
      { code: '2-5', default: false, desc: '2-5 Employees' }
    ]
    codesStore.businessTypeCodes = [
      { code: 'BIZ', default: false, desc: 'GENERAL BUSINESS' }
    ]

    wrapperFactory = propsData => {
      return shallowMount(AccountMailingAddress, {
        localVue,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory({ baseAddress: {
      city: 'Dunnville',
      country: 'CA',
      region: 'ON',
      postalCode: 'N1A 2Y5',
      street: '111-503 Main St E',
      streetAdditional: ''
    },
    viewOnlyMode: false })
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly ', () => {
    expect(wrapper.find(AccountMailingAddress).exists()).toBe(true)
  })

  it('renders proper header content', () => {
    expect(wrapper.find('[data-test="title"]').text()).toBe('Mailing Address')
  })

  it('Show edit icon when passing props', async () => {
    expect(wrapper.find('[data-test="btn-edit"]').exists()).toBe(false)
    await wrapper.setProps({ viewOnlyMode: true })
    expect(wrapper.find('[data-test="btn-edit"]').exists()).toBe(true)
  })
})
