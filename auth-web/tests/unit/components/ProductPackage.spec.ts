import { createLocalVue, mount } from '@vue/test-utils'
import ProductPackage from '@/components/auth/account-settings/product/ProductPackage.vue'
import Vuetify from 'vuetify'
import { useOrgStore } from '@/store/org'
import { useUserStore } from '@/store/user'

const vuetify = new Vuetify({})

describe('Account settings ProductPackage.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()

    const userStore = useUserStore()
    userStore.currentUser = {
      fullName: 'user2'
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
    expect(wrapper.find('h2').text()).toBe('Products and Services')
  })
})
