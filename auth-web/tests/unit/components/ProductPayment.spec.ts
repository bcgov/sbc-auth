import { Account, ProductStatus } from '@/util/constants'
import { createLocalVue, mount } from '@vue/test-utils'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import Product from '@/components/auth/common/Product.vue'
import ProductPackage from '@/components/auth/account-settings/product/ProductPayment.vue'
import Vuetify from 'vuetify'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'
import OrgService from '@/services/org.services'

const vuetify = new Vuetify({})
const pprProduct = {
  code: 'PPR',
  description: 'ppr',
  url: 'url',
  type: 'PARTNER',
  subscriptionStatus: ProductStatus.NOT_SUBSCRIBED,
  premiumOnly: false,
  parentCode: '',
  hidden: false,
  needReview: false
}

const productList = [pprProduct] as any

// vi.mock('../../../src/services/org.services')

describe('Account settings ProductPackage.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  const ob = {
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
    'AUTH_API_URL': 'https://auth-api-post-dev.pathfinder.gov.bc.ca/api/v1',
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
      name: 'test org',
      orgType: Account.PREMIUM
    }
    orgStore.productList = productList

    wrapperFactory = (propsData) => {
      return mount(ProductPackage, {
        localVue,
        vuetify,
        propsData: {
          ...propsData
        },
        mocks: {
          $t: (mock) => mock,
          $te: (mock) => mock
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

  it('emits event when checkbox is clicked non-TOS product and shows "Product Added" dialog', async () => {
    pprProduct.subscriptionStatus = ProductStatus.ACTIVE
    // useOrgStore().addOrgProducts = vi.fn().mockResolvedValue([pprProduct])
    OrgService.addProducts = vi.fn().mockResolvedValue({ data: [pprProduct] })

    wrapper.vm.isLoading = false
    await wrapper.vm.$nextTick()

    const productComponents = wrapper.findAllComponents(Product)
    expect(productComponents.length).toBe(productList.length)
    const productComponent = productComponents.at(0)

    const checkbox = productComponent.find("[data-test='check-product-PPR']")
    await checkbox.trigger('change')
    expect(checkbox.exists()).toBe(true)

    expect(productComponent.vm.productSelected).toBe(true)
    await wrapper.vm.$nextTick()

    expect(wrapper.findComponent(ModalDialog).exists()).toBe(true)
    const v = wrapper.findComponent(ModalDialog).html()
    expect(wrapper.findComponent(ModalDialog).vm.title).toBe('Product Added')
    expect(wrapper.findComponent(ModalDialog).vm.text).toBe('Your account now has access to the selected product.')
  })

  it('failed dialog', async () => {
    wrapper.vm.isLoading = false
    await wrapper.vm.$nextTick()

    const productComponents = wrapper.findAllComponents(Product)
    const productComponent = productComponents.at(0)

    const checkbox = productComponent.find("[data-test='check-product-PPR']")
    await checkbox.trigger('change')
    await wrapper.vm.$nextTick()

    expect(wrapper.findComponent(ModalDialog).exists()).toBe(true)
    expect(wrapper.findComponent(ModalDialog).vm.title).toBe('Payment Update Failed')
  })
})
