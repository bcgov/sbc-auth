import { createLocalVue, mount } from '@vue/test-utils'
import OrgService from '@/services/org.services'
import ProductPackage from '@/components/auth/account-settings/product/ProductPayment.vue'
import Vuetify from 'vuetify'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

const vuetify = new Vuetify({})

vi.mock('../../../src/services/user.services')

// vi.mock('@/services/org.services', () => ({
//   addProducts: vi.fn().mockResolvedValue({ data: null })
// }))

describe('Account settings ProductPackage.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  const ob = {
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
    'AUTH_API_URL': 'https://auth-api-post-dev.pathfinder.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(ob)

  beforeEach(() => {
    const localVue = createLocalVue()

    const userStore = useUserStore()
    userStore.currentUser = {
      fullName: 'user2',
      roles: []
    } as any
    const orgStore = useOrgStore()
    orgStore.currentOrganization = {
      name: 'test org'
    }

    wrapperFactory = (propsData) => {
      return mount(ProductPackage, {
        localVue,
        vuetify,
        propsData: {
          ...propsData
        },
        mocks: {
          $t: (mock) => mock
        }
      })
    }

    wrapper = wrapperFactory({})
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.findComponent(ProductPackage).exists()).toBe(true)
  })

  it('renders proper header content', () => {
    expect(wrapper.find('h2').text()).toBe('Products and Payment')
  })

  it('handles modal dialog add product correctly', async () => {
    const orgStore = useOrgStore()
    orgStore.currentSelectedProducts = [{ code: 'TEST_PRODUCT' }]
    wrapper.vm.addProductOnAccountAdmin = true
    const mockOpen = vi.fn()
    wrapper.vm.$refs.confirmDialog.open = mockOpen

    const addProducts = vi.spyOn(OrgService, 'addProducts').mockResolvedValue(null)

    await wrapper.vm.submitProductRequest()

    expect(addProducts).toHaveBeenCalled()
    expect(mockOpen).toHaveBeenCalled()
    expect(wrapper.vm.dialogTitle).toBe('Product Added')
    expect(wrapper.vm.dialogText).toBe('Your account now has access to the selected product.')
    expect(wrapper.vm.dialogError).toBe(false)
  })

  it('handles modal dialog failed', async () => {
    const orgStore = useOrgStore()
    orgStore.currentSelectedProducts = [{ code: 'TEST_PRODUCT' }]
    wrapper.vm.addProductOnAccountAdmin = true
    const mockOpen = vi.fn()
    wrapper.vm.$refs.confirmDialog.open = mockOpen

    const addProducts = vi.spyOn(OrgService, 'addProducts').mockRejectedValue(new Error('Failed to add products'))

    await wrapper.vm.submitProductRequest()

    expect(addProducts).toHaveBeenCalled()
    expect(mockOpen).toHaveBeenCalled()
    expect(wrapper.vm.dialogTitle).toBe('Product Request Failed')
    expect(wrapper.vm.dialogText).toBe('')
    expect(wrapper.vm.dialogError).toBe(true)
  })
})
