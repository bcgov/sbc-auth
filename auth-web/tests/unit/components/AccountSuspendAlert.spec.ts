import { createLocalVue, shallowMount } from '@vue/test-utils'
import AccountSuspendAlert from '@/components/auth/common/AccountSuspendAlert.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import CodesModule from '@/store/modules/codes'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('AccountSuspendAlert.vue', () => {
  let wrapper: any
  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const orgModule = {
      namespaced: true,
      state: { currentOrganization: {} },
      actions: {
        calculateFailedInvoices: jest.fn(() => {
          return {
            totalTransactionAmount: 10,
            totalAmountToPay: 20
          }
        })
      }
    }

    const vuetify = new Vuetify({})

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule,
        codes: CodesModule
      }
    })

    const $t = () => ''
    wrapper = shallowMount(AccountSuspendAlert, {
      store,
      localVue,
      vuetify,
      mocks: { $t }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('Should have Alert', () => {
    expect(wrapper.find('.banner-info')).toBeTruthy()
  })
})
