import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import AddBusinessDialog from '@/components/auth/manage-business/AddBusinessDialog.vue'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

const localVue = createLocalVue()
localVue.use(Vuex)

const tests = [
  {
    desc: 'renders the component properly for a CP',
    businessIdentifier: 'CP0000000',
    passcodeLabel: 'Passcode',
    certifyExists: false,
    forgotButtonText: 'I lost or forgot my passcode',
    isGovStaffAccount: false,
    userFirstName: 'Nadia',
    userLastName: 'Woodie',
  },
  {
    desc: 'renders the component properly for a BC',
    businessIdentifier: 'BC0000000',
    passcodeLabel: 'Password',
    certifyExists: false,
    forgotButtonText: 'I lost or forgot my password',
    isGovStaffAccount: false,
    userFirstName: 'Nadia',
    userLastName: 'Woodie',
  },
  {
    desc: 'renders the component properly for a FM (client User)',
    businessIdentifier: 'FM0000000',
    passcodeLabel: 'Proprietor or Partner Name (e.g., Last Name, First Name Middlename)',
    certifyExists: true,
    forgotButtonText: null,
    isGovStaffAccount: false,
    userFirstName: 'Nadia',
    userLastName: 'Woodie',
  },
  {
    desc: 'renders the component properly for a FM (staff user)',
    businessIdentifier: 'FM0000000',
    passcodeLabel: 'Proprietor or Partner Name (e.g., Last Name, First Name Middlename)',
    certifyExists: true,
    forgotButtonText: null,
    isGovStaffAccount: true,
    userFirstName: 'Nadia',
    userLastName: 'Woodie',
  },
  {
    desc: 'renders the component properly for a FM (sbc staff)',
    businessIdentifier: 'FM0000000',
    passcodeLabel: 'Proprietor or Partner Name (e.g., Last Name, First Name Middlename)',
    certifyExists: true,
    forgotButtonText: null,
    isGovStaffAccount: false,
    userFirstName: 'Nadia',
    userLastName: 'Woodie',
  }
]
tests.forEach(test => {
  describe('Add Business Form', () => {
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

      wrapper = shallowMount(AddBusinessDialog, {
        store,
        vuetify,
        propsData: { 
          dialog: true,
          isGovStaffAccount: test.isGovStaffAccount,
          userFirstName: test.userFirstName,
          userLastName: test.userLastName
        }
      })
    })

    afterAll(() => {
      wrapper.destroy()
    })

    it(test.desc, () => {
      wrapper.setData({ businessIdentifier: test.businessIdentifier })

      // verify components
      expect(wrapper.attributes('id')).toBe('add-business-dialog')
      expect(wrapper.find('#add-business-dialog').isVisible()).toBe(true)
      expect(wrapper.find(HelpDialog).exists()).toBe(true)

      // verify input fields
      expect(wrapper.find('.business-identifier').attributes('label')).toBe('Incorporation Number or Registration Number')
      expect(wrapper.find('.passcode').attributes('label')).toBe(test.passcodeLabel)
      expect(wrapper.find('.certify').exists()).toBe(test.certifyExists)
      expect(wrapper.find('.folio-number').attributes('label')).toBe('Folio or Reference Number (Optional)')
      expect(wrapper.find('.certifier').exists()).toBe(test.isGovStaffAccount)
      if (test.isGovStaffAccount) {
        expect(wrapper.find('.certifier').attributes('label')).toContain('Legal name of certified person')
      }

      // verify buttons
      if (!test.certifyExists) {
        expect(wrapper.find('#forgot-button').exists()).toBe(!!test.forgotButtonText)
      }
      if (test.forgotButtonText) {
        expect(wrapper.find('#forgot-button span').text()).toBe(test.forgotButtonText)
      }
      expect(wrapper.find('#cancel-button span').text()).toBe('Cancel')

      // always enable add button
      expect(wrapper.find('#add-button span').text()).toBe('Add')
    })
  })
})
