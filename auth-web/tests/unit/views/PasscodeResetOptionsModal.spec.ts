import { createLocalVue, mount } from '@vue/test-utils'

import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PasscodeResetOptionsModal from '@/components/auth/manage-business/PasscodeResetOptionsModal.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

const mockSession = {
  'NAME_REQUEST_URL': 'Mock Name Request URL',
  'NRO_URL': 'Mock NRO URL'
}
document.body.setAttribute('data-app', 'true')
const vuetify = new Vuetify({})
const router = new VueRouter()

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('PasscodeResetOptionsModal.vue', () => {
  let wrapper: any

  beforeEach(() => {
    const MyStub = {
      template: '<div />'
    }
    sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const localVue = createLocalVue()
    localVue.use(Vuex)

    wrapper = mount(PasscodeResetOptionsModal, {
      localVue,
      router,
      vuetify,
      mocks: {
        $t: (msg) => {
          switch (msg) {
            case 'removeBusinessOptionModalResetPasscode':
              return '<li>Business will be removed from this account</li>' +
              '<li>New business passcode will be generated and will cancel the old business passcode</li>' +
              '<li>New business passcode will be sent through email to the person who will be responsible for managing this business moving forward</li>'
            case 'removeBusinessOptionModalDonotResetPasscode':
              return '<li>Business will be removed from this account</li>' +
              '<li>The current passcode for this business will be cancelled</li><li>You will not be able to add this' +
              'business back to your account without a new passcode</li>'
            case 'removeBusinessOptionModalSubTitle':
              return 'Please select one of the two choices below to remove this business from the account'
            default:
              return ''
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
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('Donot reset passcode emits remove-business event', () => {
    wrapper.vm.isResetPasscode = false
    const spy = vi.spyOn(wrapper.vm, 'confirmPasscodeResetOptions')

    wrapper.vm.confirmPasscodeResetOptions()
    expect(spy).toBeCalled()
    const donotResetEvent = wrapper.emitted('confirm-passcode-reset-options')
    expect(donotResetEvent).toBeTruthy()
  })

  it('Reset passcode validations', () => {
    wrapper.vm.isResetPasscode = false
    wrapper.vm.emailAddress = 'test3@gmail.com'
    wrapper.vm.confirmedEmailAddress = 'test22@gmail.com'
    const result = wrapper.vm.emailMustMatch()
    expect(result).toEqual('Email addresses must match')
  })

  it('Reset passcode emits remove-business event', () => {
    const emailValue = 'test1@gmail.com'
    wrapper.vm.isResetPasscode = true
    wrapper.vm.emailAddress = emailValue
    wrapper.vm.confirmedEmailAddress = emailValue

    const stub = vi.fn().mockImplementation(() => {
      return true
    })
    wrapper.setMethods({ isFormValid: stub })
    const spy = vi.spyOn(wrapper.vm, 'confirmPasscodeResetOptions')

    wrapper.vm.confirmPasscodeResetOptions()
    expect(spy).toBeCalled()
    const resetEvent = wrapper.emitted('confirm-passcode-reset-options')
    expect(resetEvent).toBeTruthy()
    expect(resetEvent[0]).toEqual([emailValue])
  })
})
