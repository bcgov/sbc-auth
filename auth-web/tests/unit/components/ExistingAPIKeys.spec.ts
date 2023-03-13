import { createLocalVue, mount } from '@vue/test-utils'

import ExistingAPIKeys from '@/components/auth/account-settings/advance-settings/ExistingAPIKeys.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import { nextTick } from 'vue/types/umd'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')
const consumerKey = [
  {
    'apiAccess': [
      'ALL_API'
    ],
    'apiKey': '5j0YIMvBTP5qGqh1VPxkkPicFACknqtI',
    'apiKeyName': 'key1',
    'environment': 'non-prod',
    'keyExpiryDate': 'never',
    'keyStatus': 'approved'
  }
]
describe('Account settings ExistingAPIKeys.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  const $t = () => 'test trans data'
  const apikeyList = {
    'consumer': {
      'consumerKey': consumerKey,
      'consumerStatus': 'approved'
    }
  }
  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const orgModule = {
      namespaced: true,
      actions: {
        getOrgApiKeys: jest.fn(() => {
          return apikeyList
        })
      },
      state: {
        currentOrganization: {
          id: 123,
          name: 'test org'
        }

      }
    }

    const store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule

      }
    })

    wrapperFactory = (propsData) => {
      return mount(ExistingAPIKeys, {
        store,
        localVue,
        vuetify,
        mocks: { $t },
        propsData: {
          ...propsData
        },
        stubs: {
          'v-btn': {
            template: `<button @click='$listeners.click'></button>`
          },
          ModalDialog: true
        }
      })
    }

    wrapper = wrapperFactory({})
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.find(ExistingAPIKeys).exists()).toBe(true)
  })

  it('renders proper header ', () => {
    expect(wrapper.find('h2').text()).toBe('Existing API Keys')
  })

  it('Should have data table', async () => {
    await wrapper.vm.loadApiKeys()
    expect(wrapper.find('.apikey-list')).toBeTruthy()
    expect(wrapper.find('[data-test="confirm-button-key1"]').exists()).toBe(true)
  })

  it('Should open Confirmation modal on revoke button click', async () => {
    await wrapper.vm.loadApiKeys()
    const stub = jest.fn(() => consumerKey)
    wrapper.setMethods({ confirmationModal: stub })

    wrapper.find('[data-test="confirm-button-key1"]').trigger('click')
    await Vue.nextTick()
    await Vue.nextTick()

    expect(wrapper.vm.confirmationModal).toBeCalled()
    expect(wrapper.find("[data-test='confirmation-modal']").exists()).toBe(true)
  })
})
