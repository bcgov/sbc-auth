import { LoginSource, Permission } from '@/util/constants'
import { createLocalVue, mount } from '@vue/test-utils'
import CodesService from '@/services/codes.service'
import ProductPackage from '@/components/auth/account-settings/product/ProductPayment.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

const vuetify = new Vuetify({})

vi.mock('../../../src/services/user.services')
vi.mock('../../../src/services/org.services')

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
    localVue.use(VueRouter)
    const router = new VueRouter()

    const userStore = useUserStore()
    userStore.currentUser = {
      fullName: 'user2',
      roles: [],
      loginSource: LoginSource.BCSC
    } as any
    const orgStore = useOrgStore()
    orgStore.permissions = [Permission.VIEW_REQUEST_PRODUCT_PACKAGE]
    orgStore.currentOrganization = {
      name: 'test org'
    }
    orgStore.syncAddress = () => {
      return Promise.resolve()
    }
    orgStore.getOrgProducts = () => {
      return Promise.resolve([])
    }
    orgStore.getOrgPayments = () => {
      return Promise.resolve([]) as any
    }
    orgStore.addOrgProducts = () => {
      return Promise.resolve() as any
    }
    CodesService.getProductPaymentMethods = vi.fn().mockResolvedValue({
      data: []
    })
    wrapperFactory = (propsData) => {
      return mount(ProductPackage, {
        localVue,
        router,
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
    orgStore.addOrgProducts = () => {
      return Promise.resolve() as any
    }
    await wrapper.vm.$nextTick()
    orgStore.currentSelectedProducts = [{ code: 'TEST_PRODUCT' }]
    wrapper.vm.addProductOnAccountAdmin = true
    const mockOpen = vi.fn()
    wrapper.vm.$refs.confirmDialog.open = mockOpen

    await wrapper.vm.submitProductRequest()
    expect(mockOpen).toHaveBeenCalled()
    expect(wrapper.vm.dialogTitle).toBe('Product Added')
    expect(wrapper.vm.dialogText).toBe('Your account now has access to the selected product.')
    expect(wrapper.vm.dialogError).toBe(false)
  })

  it('handles modal dialog failed', async () => {
    const orgStore = useOrgStore()
    orgStore.addOrgProducts = () => {
      throw Error('bad')
    }
    wrapper = wrapperFactory({})
    orgStore.currentSelectedProducts = [{ code: 'TEST_PRODUCT' }]
    wrapper.vm.addProductOnAccountAdmin = true
    const mockOpen = vi.fn()
    wrapper.vm.$refs.confirmDialog.open = mockOpen

    await wrapper.vm.submitProductRequest()
    expect(mockOpen).toHaveBeenCalled()
    expect(wrapper.vm.dialogTitle).toBe('Product Request Failed')
    expect(wrapper.vm.dialogText).toBe('')
    expect(wrapper.vm.dialogError).toBe(true)
  })
})
