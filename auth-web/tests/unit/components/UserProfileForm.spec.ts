import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import TermsOfUseDialog from '@/components/auth/common/TermsOfUseDialog.vue'
import UserProfileForm from '@/components/auth/create-account/UserProfileForm.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('UserProfileForm.vue', () => {
  let wrapper: Wrapper<UserProfileForm>
  let vuetify
  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  let userModule: any

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)
  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    vuetify = new Vuetify()
    const $t = () => 'test'

    userModule = {
      namespaced: true,
      state: {
        userProfile: {
        }
      },
      actions: {
        getUserProfile: vi.fn()
      }
    }

    const store = new Vuex.Store({
      strict: false,
      modules: {
        user: userModule
      }
    })

    wrapper = mount(UserProfileForm, {
      store,
      localVue,
      vuetify,
      mocks: { $t },
      stubs: {
        ModalDialog: true,
        TermsOfUseDialog: true
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

  it('user profile form has save and cancel buttons', () => {
    expect(wrapper.find('.save-continue-button')).toBeTruthy()
    expect(wrapper.find('.cancel-button')).toBeTruthy()
  })

  it('first name is empty', () => {
    expect(wrapper.vm.$data.firstName).toBe('')
  })

  it('last name is empty', () => {
    expect(wrapper.vm.$data.lastName).toBe('')
  })

  it('email data is empty', () => {
    expect(wrapper.vm.$data.emailAddress).toBe('')
  })

  it('confirm email data is empty', () => {
    expect(wrapper.vm.$data.confirmedEmailAddress).toBe('')
  })

  it('confirm phone data is empty', () => {
    expect(wrapper.vm.$data.phoneNumber).toBe('')
  })

  it('confirm extension data to be empty', () => {
    expect(wrapper.vm.$data.extension).toBe('')
  })
})
