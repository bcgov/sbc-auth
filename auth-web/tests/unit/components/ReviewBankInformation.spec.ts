import { createLocalVue, mount } from '@vue/test-utils'
import { Account } from '@/util/constants'
import OrgModule from '@/store/modules/org'
import PADInfoForm from '@/components/auth/common/PADInfoForm.vue'
import ReviewBankInformation from '@/components/auth/account-freeze/ReviewBankInformation.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import TermsOfUseDialog from '@/components/auth/common/TermsOfUseDialog.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import can from '@/directives/can'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('ReviewBankInformation.vue', () => {
  let wrapper: any
  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.directive('can', can)

    const vuetify = new Vuetify({})

    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {}
      },
      actions: {
        getOrgPayments: vi.fn(),
        updateOrg: vi.fn(),
        updatePadInfo: vi.fn(),
        validatePADInfo: vi.fn()
      },
      mutations: {},
      getters: {}
    }

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule
      }
    })

    wrapper = mount(ReviewBankInformation, {
      store,
      localVue,
      vuetify,
      mixins: [Steppable],
      components: {
        PADInfoForm,
        TermsOfUseDialog
      }
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

  it('should render pad component title', () => {
    expect(wrapper.find('[data-test="pad-info-form-title"]').text()).toBe('Banking Information')
    expect(wrapper.find('[data-test="pad-info-form-title"]').exists()).toBe(true)
  })

  it('should render pad component inputs', () => {
    expect(wrapper.findAll('.v-input').length).toBe(3)
  })

  it('should set pad valid', () => {
    expect(wrapper.vm.padValid).toBe(false)
    wrapper.vm.isPADValid(true)
    expect(wrapper.vm.padValid).toBe(true)
  })

  it('should render next and back buttons', () => {
    expect(wrapper.find('[data-test="next"]')).toBeTruthy()
    expect(wrapper.find('[data-test="next"]').text()).toEqual('Next')
    expect(wrapper.find('[data-test="back"]')).toBeTruthy()
    expect(wrapper.find('[data-test="back"]').text()).toEqual('Back')
  })
})
