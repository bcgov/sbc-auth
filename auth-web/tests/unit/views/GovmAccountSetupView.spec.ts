import { createLocalVue, mount } from '@vue/test-utils'

import GovmAccountSetupView from '@/views/auth/create-account/GovmAccountSetupView.vue'
// import { AccountStatus } from '@/util/constants'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'

import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import displayMode from '@/directives/displayMode'
import Vuelidate from 'vuelidate'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(Vuelidate)
const router = new VueRouter()
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('GovmAccountSetupView.vue', () => {
  let wrapper: any

  beforeEach(async () => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.directive('displayMode', displayMode)

    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
          name: 'test org'
        },
        currentOrgAddress: {
          city: 'city',
          street: 'street'
        },
        currentMembership: [{
          membershipTypeCode: 'OWNER',
          membershipStatus: 'ACTIVE',
          user: { username: 'test' } }],
        pendingOrgMembers: []
      },
      actions: {
      },
      mutations: {
        setCurrentOrganizationAddress: jest.fn(),
        resetInvitations: jest.fn()
      }
    }

    const codeModule = {
      namespaced: true,
      state: {},
      actions: { getBusinessTypeCodes: jest.fn(() => []),
        getBusinessSizeCodes: jest.fn(() => [])
      }
    }

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule,
        codes: codeModule
      }
    })

    wrapper = mount(GovmAccountSetupView, {
      store,
      localVue,
      router,
      vuetify,
      mocks: {
        $t: (mock) => mock
      }
    })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('GovmAccountSetupView is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('should render with h1', () => {
    expect(wrapper.find('h1').text()).toBe('Create a Ministry Account')
  })

  it('should render page title icon color correctly', () => {
    expect(wrapper.findComponent(ModalDialog).exists()).toBe(true)
  })

  it('should call createAccount on emit', async () => {
    wrapper.vm.$emit('createAccount')

    await wrapper.vm.$nextTick() // Wait until $emits have been handled

    // assert event has been emitted
    expect(wrapper.emitted().createAccount).toBeTruthy()
  })
})
