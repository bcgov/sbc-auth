
import { createLocalVue, shallowMount } from '@vue/test-utils'
import { useOrgStore, useUserStore } from '@/stores'
import SelectProductService from '@/components/auth/create-account/SelectProductService.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('SelectProductService.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)

    const userStore = useUserStore()
    userStore.currentUser = { 'userName': 'user1' } as any

    const orgStore = useOrgStore()
    orgStore.currentOrganization = { } as any
    orgStore.productList = [
      {
        'code': 'PPR',
        'name': 'Personal Property Registry',
        'description': 'test',
        'url': 'https://test.com/ppr',
        'type': 'INTERNAL',
        'mdiIcon': 'mdi-image-outline'
      },
      {
        'code': 'VS',
        'name': 'Wills Registry',
        'description': 'VS',
        'url': 'https://test.com/vs',
        'type': 'PARTNER',
        'mdiIcon': 'mdi-image-outline'
      }
    ] as any
    orgStore.currentSelectedProducts = ['VS']

    const router = new VueRouter()

    wrapperFactory = (propsData) => {
      return shallowMount(SelectProductService, {
        localVue,
        router,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory({ userProfile: {} })
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly and address is being shown', () => {
    expect(wrapper.find(SelectProductService).exists()).toBe(true)
  })
})
