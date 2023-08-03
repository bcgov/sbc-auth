import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import ManageBusinessDialog from '@/components/auth/manage-business/ManageBusinessDialog.vue'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

const localVue = createLocalVue()
localVue.use(Vuex)

const testCaseList = [
  {
    description: 'Should render for a BC account',
    businessIdentifier: 'BC0000000',
    passcodeInputLabel: 'Password',
    certifyExists: false,
    forgotButtonLabel: 'Help',
    isGovStaffAccount: false
  },
  {
    description: 'Should render for a CP account',
    businessIdentifier: 'CP0000000',
    passcodeInputLabel: 'Passcode',
    certifyExists: false,
    forgotButtonLabel: 'Help',
    isGovStaffAccount: false
  },
  {
    description: 'Should render for a FM Client account',
    businessIdentifier: 'FM0000000',
    passcodeInputLabel: 'Proprietor or Partner Name (e.g., Last Name, First Name Middlename)',
    certifyExists: true,
    forgotButtonLabel: null,
    isGovStaffAccount: false
  },
  {
    description: 'Should render for a FM Staff account',
    businessIdentifier: 'FM0000000',
    passcodeInputLabel: 'Proprietor or Partner Name (e.g., Last Name, First Name Middlename)',
    certifyExists: true,
    forgotButtonLabel: null,
    isGovStaffAccount: false
  },
  {
    description: 'Should render for a FM SBC Staff account',
    businessIdentifier: 'FM0000000',
    passcodeInputLabel: 'Proprietor or Partner Name (e.g., Last Name, First Name Middlename)',
    certifyExists: true,
    forgotButtonLabel: null,
    isGovStaffAccount: false
  }
]

testCaseList.forEach(testCase => {
  describe('ManageBusinessDialog Component', () => {
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
          dialog: true,
          isGovStaffAccount: testCase.isGovStaffAccount
        }
      })
    })

    afterAll(() => {
      wrapper.destroy()
    })

    it(testCase.description, async () => {
      wrapper.setData({
        businessIdentifier: testCase.businessIdentifier,
        businessName: 'My Business Inc'
      })
      await flushPromises()
      // parent component
      expect(wrapper.attributes('id')).toBe('manage-business-dialog')
      expect(wrapper.find('#manage-business-dialog').isVisible()).toBe(true)
      expect(wrapper.findComponent(HelpDialog).exists()).toBe(true)
      // input components
      expect(wrapper.find('.passcode').attributes('label')).toBe(testCase.passcodeInputLabel)
      expect(wrapper.find('.certify').exists()).toBe(testCase.certifyExists)
      expect(wrapper.find('.authorization').exists()).toBe(testCase.isGovStaffAccount)
      if (testCase.isGovStaffAccount) {
        expect(wrapper.find('.authorization').attributes('label')).toContain('Legal name of Authorized Person')
      }
      // button components
      expect(wrapper.find('#cancel-button span').text()).toBe('Cancel')
      expect(wrapper.find('#add-button span').text()).toBe('Manage This Business')
      if (!testCase.certifyExists) {
        expect(wrapper.find('#forgot-button').exists()).toBe(!!testCase.forgotButtonLabel)
      }
      if (testCase.forgotButtonLabel) {
        expect(wrapper.find('#forgot-button span').text()).toBe(testCase.forgotButtonLabel)
      }
    })
  })
})
