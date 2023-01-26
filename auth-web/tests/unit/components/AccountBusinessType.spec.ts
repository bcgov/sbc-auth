import { createLocalVue, mount } from '@vue/test-utils'

import { Account } from '@/util/constants'
import AccountBusinessType from '@/components/auth/common/AccountBusinessType.vue'
import CodesModule from '@/store/modules/codes'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import can from '@/directives/can'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)
Vue.use(VueRouter)

document.body.setAttribute('data-app', 'true')

describe('AccountBusinessType.vue', () => {
  let orgModule: any
  let codesModule: any
  let wrapper: any
  let store: any
  const localVue = createLocalVue()
  localVue.directive('can', can)
  localVue.use(Vuex)
  const vuetify = new Vuetify({})

  beforeEach(() => {
    codesModule = {
      namespaced: true,
      state: {
      },
      actions: CodesModule.actions,
      mutations: CodesModule.mutations,
      getters: CodesModule.getters
    }

    orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
          name: '',
          orgType: Account.BASIC
        }
      }
    }
    store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule,
        codes: codesModule
      }
    })
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    const $t = () => ''
    wrapper = mount(AccountBusinessType, {
      store,
      localVue,
      vuetify,
      propsData: {
        govmAccount: false
      },
      mocks: { $t
      }
    })
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('individual account type rendering', async () => {
    const $t = () => ''
    wrapper = mount(AccountBusinessType, {
      store,
      localVue,
      vuetify,
      propsData: {
        govmAccount: false
      },
      mocks: { $t
      }
    })
    await wrapper.setData({ isLoading: false })
    expect(wrapper.find("[data-test='account-name']").exists()).toBeTruthy()
    expect(wrapper.find("[data-test='input-branch-name']").isVisible()).toBeFalsy()
    expect(wrapper.find("[data-test='business-account-type-details']").exists()).toBeFalsy()
  })

  it('business account type rendering', async () => {
    const $t = () => ''
    wrapper = mount(AccountBusinessType, {
      store,
      localVue,
      vuetify,
      propsData: {
        govmAccount: false
      },
      mocks: { $t
      }
    })
    await wrapper.setData({ isLoading: false })
    wrapper.find("[data-test='radio-business-account-type']").trigger('click')
    await flushPromises()
    expect(wrapper.find("[data-test='input-branch-name']").isVisible()).toBeTruthy()
    expect(wrapper.find("[data-test='business-account-type-details']").exists()).toBeTruthy()
  })
})
