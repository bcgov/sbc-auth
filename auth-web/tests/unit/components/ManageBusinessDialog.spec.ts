import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import ManageBusinessDialog from '@/components/auth/manage-business/ManageBusinessDialog.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

const localVue = createLocalVue()
localVue.use(Vuex)

const tests = [
  {
    description: 'Should render Manage Business Dialog component'
  }
]

tests.forEach(test => {
  describe('Manage Business Form', () => {
    let wrapper: Wrapper<any>

    beforeAll(() => {
      const orgModule = {
        namespaced: true,
        state: {
          currentOrganization: {
            name: 'new org'
          }
        }
      }

      const businessModule = {
        namespaced: true,
        state: {

        },
        action: {
          addBusiness: jest.fn(),
          updateBusinessName: jest.fn(),
          updateFolioNumber: jest.fn()
        }
      }

      const store = new Vuex.Store({
        strict: false,
        modules: {
          org: orgModule,
          business: businessModule
        }
      })

      wrapper = shallowMount(ManageBusinessDialog, {
        store,
        vuetify,
        propsData: {
          dialog: true
        }
      })
    })

    afterAll(() => {
      wrapper.destroy()
    })

    it(test.description, async () => {
      wrapper.setData({
        businessName: 'My Business Inc'
      })
      await flushPromises()

      expect(wrapper.attributes('id')).toBe('manage-business-dialog')
      expect(wrapper.find('#manage-business-dialog').isVisible()).toBe(true)
    })
  })
})
