import { createLocalVue, mount, shallowMount } from '@vue/test-utils'

import { AccountBusinessType } from '@/util/constants'
import AccountInformationBusinessType from '@/components/auth/common/AccountInformationBusinessType.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import can from '@/directives/can'

Vue.use(Vuetify)
Vue.use(VueRouter)

document.body.setAttribute('data-app', 'true')

describe('AccountInformationBusinessType.vue', () => {
  let orgModule: any
  let wrapper: any
  let store: any
  const localVue = createLocalVue()
  localVue.directive('can', can)
  localVue.use(Vuex)
  const vuetify = new Vuetify({})

  beforeEach(() => {
    orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
          name: ''
        }
      }
    }
    store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule
      }
    })
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    const $t = () => ''
    wrapper = mount(AccountInformationBusinessType, {
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

  it('individual account type rendering', () => {
    const $t = () => ''
    wrapper = mount(AccountInformationBusinessType, {
      store,
      localVue,
      vuetify,
      propsData: {
        govmAccount: false
      },
      mocks: { $t
      }
    })

    expect(wrapper.find("[data-test='account-name']").exists()).toBeTruthy()
    expect(wrapper.find("[data-test='branch-detail']").exists()).toBeFalsy()
    expect(wrapper.find("[data-test='business-account-type-details']").exists()).toBeFalsy()
  })

  it('business account type rendering', () => {
    const $t = () => ''
    wrapper = mount(AccountInformationBusinessType, {
      store,
      localVue,
      vuetify,
      propsData: {
        govmAccount: false
      },
      mocks: { $t
      }
    })

    wrapper.find("[data-test='radio-business-account-type']").trigger('click')
    expect(wrapper.find("[data-test='branch-detail']").exists()).toBeTruthy()
    expect(wrapper.find("[data-test='business-account-type-details']").exists()).toBeTruthy()
  })
})
