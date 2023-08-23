import { createLocalVue, shallowMount } from '@vue/test-utils'
import AccountCreateBasic from '@/components/auth/create-account/AccountCreateBasic.vue'
import BaseAddressForm from '@/components/auth/common/BaseAddressForm.vue'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import { useOrgStore } from '@/store/org'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccountCreateBasic.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    localVue.use(Vuex)
    const router = new VueRouter()
    sessionStorage[SessionStorageKeys.LaunchDarklyFlags] =
      JSON.stringify({
        'payment-type-in-account-creation': true,
        'auth-options-learn-more': true,
        'enable-ltd-and-ulc-affiliate': true
      })
    const orgStore = useOrgStore()
    orgStore.currentOrganization = {
      name: 'test org'
    } as any
    orgStore.currentMembership = [{
      membershipTypeCode: 'OWNER',
      membershipStatus: 'ACTIVE',
      user: { username: 'test' }
    }] as any

    // Remove with Vue 3 upgrade
    // We need a store for this one it calls auth/currentLoginSource - which is in sbc-common-components for now.
    const store = new Vuex.Store({
      state: {},
      strict: false
    })

    wrapperFactory = (propsData) => {
      return shallowMount(AccountCreateBasic, {
        localVue,
        router,
        store,
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
    expect(wrapper.find(AccountCreateBasic).exists()).toBe(true)
    expect(wrapper.find(BaseAddressForm).exists()).toBe(true)
    expect(wrapper.find('.save-btn').is('[disabled]')).toBe(true)
  })
})
