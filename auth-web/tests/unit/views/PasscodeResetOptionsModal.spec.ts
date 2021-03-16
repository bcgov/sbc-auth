import { createLocalVue, mount } from '@vue/test-utils'

import PasscodeResetOptionsModal from '@/components/auth/manage-business/PasscodeResetOptionsModal.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

const mockSession = {
  'NRO_URL': 'Mock NRO URL',
  'NAME_REQUEST_URL': 'Mock Name Request URL'
}

Vue.use(Vuetify)
Vue.use(VueRouter)
document.body.setAttribute('data-app', 'true')

const router = new VueRouter()
const vuetify = new Vuetify({})

describe('PasscodeResetOptionsModal.vue', () => {
  let wrapper: any

  beforeEach(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const localVue = createLocalVue()
    localVue.use(Vuex)
    const MyStub = {
      template: '<div />'
    }

    wrapper = mount(PasscodeResetOptionsModal, {
      localVue,
      router,
      vuetify,
      mocks: {
        $t: (msg) => {
          switch (msg) {
            case 'removeBusinessOptionModalResetPasscode':
              return '<li>Business will be removed from this account</li><li>New business passcode will be generated and will cancel the old business passcode</li><li>New business passcode will be sent through email to the person who will be responsible for managing this business moving forward</li>'
            case 'removeBusinessOptionModalDonotResetPasscode':
              return '<li>Business will be removed from this account</li><li>The current passcode for this business will be cancelled</li><li>You will not be able to add this business back to your account without a new passcode</li>'
            case 'removeBusinessOptionModalSubTitle':
              return 'Please select one of the two choices below to remove this business from the account'
          }
        }
      },
      stubs: {
        'v-form': MyStub,
        'v-btn': {
          template: `<button @click='$listeners.click'></button>`
        }
      }
    })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('boilerplate validation', () => {
    wrapper.vm.isDialogOpen = true

    expect(wrapper.find("[data-test='dialog-remove-business-options']").exists()).toBe(true)
    expect(wrapper.find("[data-test='text-donot-reset-passcode-summary']").exists()).toBe(true)
    expect(wrapper.find("[data-test='text-reset-passcode-summary']").exists()).toBe(true)
    expect(wrapper.vm.isResetPasscode).toBeFalsy()
  })

  it('Donot reset passcode emits remove-business event', () => {
    wrapper.vm.isDialogOpen = true
    wrapper.vm.isResetPasscode = false
    const spy = jest.spyOn(wrapper.vm, 'confirmPasscodeResetOptions')

    wrapper.find("[data-test='btn-reset-passcode']").trigger('click')
    expect(spy).toBeCalled()
    expect(wrapper.emitted('confirm-passcode-reset-options')).toBeTruthy()
    expect(wrapper.emitted('confirm-passcode-reset-options')[0]).toEqual([null])
  })

  it('Reset passcode validations', () => {
    wrapper.vm.isDialogOpen = true
    wrapper.vm.isResetPasscode = false
    wrapper.vm.emailAddress = 'test1@gmail.com'
    wrapper.vm.confirmedEmailAddress = 'test2@gmail.com'
    const result = wrapper.vm.emailMustMatch()
    expect(result).toEqual('Email addresses must match')
  })

  it('Reset passcode emits remove-business event', () => {
    wrapper.vm.isDialogOpen = true
    wrapper.vm.isResetPasscode = true
    wrapper.vm.emailAddress = 'test1@gmail.com'
    wrapper.vm.confirmedEmailAddress = 'test1@gmail.com'

    const stub = jest.fn().mockImplementation(() => { return true })
    wrapper.setMethods({ isFormValid: stub })
    const spy = jest.spyOn(wrapper.vm, 'confirmPasscodeResetOptions')

    wrapper.find("[data-test='btn-reset-passcode']").trigger('click')
    expect(spy).toBeCalled()
    expect(wrapper.emitted('confirm-passcode-reset-options')).toBeTruthy()
    expect(wrapper.emitted('confirm-passcode-reset-options')[0]).toEqual(['test1@gmail.com'])
  })
})
