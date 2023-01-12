import { createLocalVue, mount } from '@vue/test-utils'
import PADInfoForm from '@/components/auth/common/PADInfoForm.vue'
import TermsOfUseDialog from '@/components/auth/common/TermsOfUseDialog.vue'
import can from '@/directives/can'
import { axios } from '@/util/http-util'
import sinon from 'sinon'
import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

// @ts-ignore
Vue.use(VueCompositionAPI)
Vue.use(Vuetify)

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('PADInfoForm.vue', () => {
  let wrapper: any
  let sandbox
  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  const startingOrgPADInfo = {
    'bankAccountNumber': '1234567',
    'bankInstitutionNumber': '001',
    'bankTransitNumber': '00720',
    'isAcknowledged': true,
    'isTOSAccepted': true
  }

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.directive('can', can)

    const vuetify = new Vuetify({})

    // stub get toc get call
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(new Promise(resolve => resolve({ data: null })))

    const userModule = {
      namespaced: true,
      state: {
        userHasToAcceptTOS: false
      },
      actions: {
        getTermsOfUse: jest.fn(() => null)
      },
      mutations: {},
      getters: {}
    }

    const orgModule = {
      namespaced: true,
      state: {
        currentOrgPADInfo: { ...startingOrgPADInfo }
      },
      actions: { updatePadInfo: jest.fn() }
    }

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule,
        user: userModule
      }
    })

    wrapper = mount(PADInfoForm, {
      store,
      localVue,
      vuetify,
      propsData: {
        isAcknowledgeNeeded: false
      }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
    sandbox.restore()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()    
  })
  it('renders with base values', () => {
    expect(wrapper.find(PADInfoForm).exists()).toBe(true)
    expect(wrapper.find(TermsOfUseDialog).exists()).toBe(true)
    expect(wrapper.find('.v-form').exists()).toBe(true)
    expect(wrapper.find('.v-form').text()).toContain('Banking Information')
    expect(wrapper.find('.v-btn.help-btn').exists()).toBe(true)
    expect(wrapper.find('.bank-info-dialog-content').exists()).toBe(false)
    expect(wrapper.find('.bank-information').exists()).toBe(true)
    expect(wrapper.find('.tos-needed').exists()).toBe(true)
    // is valid
    expect(wrapper.emitted('is-pre-auth-debit-form-valid').length).toBe(1)
    expect(wrapper.emitted('is-pre-auth-debit-form-valid')[0]).toEqual([true])
  })
  it('displays help info when clicked', async () => {
    expect(wrapper.find('.bank-info-dialog-content').exists()).toBe(false)
    expect(wrapper.vm.bankInfoDialog).toBe(false)
    wrapper.find('.v-btn.help-btn').trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.bankInfoDialog).toBe(true)
    expect(wrapper.find('.bank-info-dialog-content').exists()).toBe(true)
  })
  it('displays bank fields with store values', () => {
    const bankInfoBlock = wrapper.find('.bank-information')
    const bankFields = bankInfoBlock.findAll('.v-text-field')
    expect(bankFields.length).toBe(3)
    expect(bankFields.at(0).text()).toContain('Transit Number')
    expect(bankFields.at(0).find('input').element.value).toBe(startingOrgPADInfo.bankTransitNumber)
    expect(bankFields.at(1).text()).toContain('Institution Number')
    expect(bankFields.at(1).find('input').element.value).toBe(startingOrgPADInfo.bankInstitutionNumber)
    expect(bankFields.at(2).text()).toContain('Account Number')
    expect(bankFields.at(2).find('input').element.value).toBe(startingOrgPADInfo.bankAccountNumber)
  })
  it('updates correctly', async () => {
    const bankInfoBlock = wrapper.find('.bank-information')
    const bankFields = bankInfoBlock.findAll('.v-text-field')
    expect(wrapper.vm.isTOSAccepted).toBe(true)
    bankFields.at(0).find('input').setValue('12345')
    await Vue.nextTick()
    bankFields.at(1).trigger('click')
    await Vue.nextTick()
    // assert it did not clear the other values
    expect(bankFields.at(1).find('input').element.value).toBe(startingOrgPADInfo.bankInstitutionNumber)
    expect(bankFields.at(2).find('input').element.value).toBe(startingOrgPADInfo.bankAccountNumber)
    // should have reset the tos
    expect(wrapper.vm.isTOSAccepted).toBe(false)
    expect(wrapper.emitted('is-pre-auth-debit-form-valid').length).toBe(2)
    expect(wrapper.emitted('is-pre-auth-debit-form-valid')[1]).toEqual([false])
  })
})
