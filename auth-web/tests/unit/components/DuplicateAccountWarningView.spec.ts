import { createLocalVue, mount, shallowMount } from '@vue/test-utils'

import { AccountStatus } from '@/util/constants'
import DuplicateAccountWarningView from '@/views/auth/create-account/DuplicateAccountWarningView.vue'
import { OrgWithAddress } from '@/models/Organization'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import can from '@/directives/can'

Vue.use(Vuetify)
Vue.use(VueRouter)

document.body.setAttribute('data-app', 'true')

describe('DuplicateAccountWarningView.vue', () => {
  let orgModule: any
  let userModule: any
  let wrapper: any
  let store: any
  const localVue = createLocalVue()
  localVue.directive('can', can)
  localVue.use(Vuex)
  const vuetify = new Vuetify({})

  beforeEach(() => {
    userModule = {
      namespaced: true,
      state: {
        currentUserAccountSettings: [
          {
            accountStatus: 'ACTIVE',
            accountType: 'BASIC',
            id: 2446,
            label: 'DEV SK OB1',
            productSettings: '/account/2446/settings/product-settings',
            type: 'ACCOUNT',
            urlorigin: 'https://dev.bcregistry.ca/business/auth',
            urlpath: '/account/2446/settings'
          }
        ]
      }
    }
    orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
          name: 'DEV SK OB1',
          statusCode: AccountStatus.ACTIVE,
          orgStatus: AccountStatus.ACTIVE
        }
      },
      actions: {
        addOrgSettings: jest.fn(),
        syncOrganization: jest.fn(),
        getOrgAdminContact: jest.fn().mockImplementation(scalar => {
          return { city: 'Halifax',
            country: 'CA',
            created: '2021-05-14T23:53:58.711541',
            createdBy: 'BCREGTEST Bena TEST',
            modified: '2021-05-14T23:53:58.711556',
            postalCode: 'B3J 3R4',
            region: 'NS',
            street: '111-5657 Spring Garden Rd',
            streetAdditional: ''
          }
        })
      }
    }

    store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule,
        user: userModule
      }
    })
    jest.resetModules()
    jest.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    const $t = () => ''
    wrapper = mount(DuplicateAccountWarningView, {
      store,
      localVue,
      vuetify,
      stubs: {
      },
      mocks: { $t
      }
    })
    expect(wrapper.vm).toBeTruthy()
  })

  it('data displayed is valid', async () => {
    const $t = () => ''
    const orgOfUser: OrgWithAddress = {
      id: 2446,
      name: 'DEV SK OB1',
      addressLine: '111-5657 Spring Garden Rd Halifax NS B3J 3R4 CA'
    }
    wrapper = shallowMount(DuplicateAccountWarningView, {
      store,
      localVue,
      vuetify,
      stubs: {
      },
      mocks: { $t
      }
    })
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.vm.orgsOfUser[0].id).toBe(orgOfUser.id)
    expect(wrapper.vm.orgsOfUser[0].name).toBe(orgOfUser.name)
    expect(wrapper.vm.orgsOfUser[0].addressLine).toBe(orgOfUser.addressLine)
  })

  it('valid button clicks', async () => {
    const $t = () => ''
    wrapper = shallowMount(DuplicateAccountWarningView, {
      store,
      localVue,
      vuetify,
      stubs: {
        'v-btn': {
          template: `<button @click='$listeners.click'></button>`
        }
      },
      mocks: { $t
      }
    })
    await Vue.nextTick()
    await Vue.nextTick()
    const stub = jest.fn()
    wrapper.setMethods({ navigateToRedirectUrl: stub })
    wrapper.find("[data-test='goto-access-account-button']").trigger('click')
    expect(wrapper.vm.navigateToRedirectUrl).toBeCalled()

    wrapper.setMethods({ createAccount: stub })
    wrapper.find("[data-test='goto-create-account-button']").trigger('click')
    expect(wrapper.vm.createAccount).toBeCalled()
  })
})
