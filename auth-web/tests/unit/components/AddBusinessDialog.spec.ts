import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import ManageBusinessDialog from '@/components/auth/manage-business/ManageBusinessDialog.vue'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'

// @ts-ignore
Vue.use(VueCompositionAPI)
Vue.use(Vuetify)

const vuetify = new Vuetify({})

const localVue = createLocalVue()
localVue.use(Vuex)

const testCaseList = [
  {
    description: 'Should render for a BC account',
    businessIdentifier: 'CP0000000',
    passcodeInputLabel: 'Passcode',
    certifyExists: false,
    passcodeExists: true,
    folioNumberExists: true,
    forgotButtonText: 'I lost or forgot my passcode',
    isStaffOrSbcStaff: false,
    userFirstName: 'Nadia',
    userLastName: 'Woodie'
  },
  {
    description: 'Should render for a CP account',
    businessIdentifier: 'BC0000000',
    passcodeInputLabel: 'Password',
    certifyExists: false,
    passcodeExists: true,
    folioNumberExists: true,
    forgotButtonText: 'I lost or forgot my password',
    isStaffOrSbcStaff: false,
    userFirstName: 'Nadia',
    userLastName: 'Woodie'
  },
  {
    description: 'Should render for a FM Client account',
    businessIdentifier: 'FM0000000',
    passcodeInputLabel: 'Proprietor or Partner Name (e.g., Last Name, First Name Middlename)',
    certifyExists: true,
    passcodeExists: true,
    folioNumberExists: true,
    forgotButtonText: null,
    isStaffOrSbcStaff: false,
    userFirstName: 'Nadia',
    userLastName: 'Woodie'
  },
  {
    description: 'Should render for a FM Staff account',
    businessIdentifier: 'FM0000000',
    certifyExists: false,
    passcodeExists: false,
    folioNumberExists: false,
    forgotButtonText: null,
    isStaffOrSbcStaff: true,
    userFirstName: 'Nadia',
    userLastName: 'Woodie'
  },
  {
    description: 'Should render for a FM SBC Staff account',
    businessIdentifier: 'FM0000000',
    certifyExists: false,
    passcodeExists: false,
    folioNumberExists: false,
    forgotButtonText: null,
    isStaffOrSbcStaff: true,
    userFirstName: 'Nadia',
    userLastName: 'Woodie'
  }
]
testCaseList.forEach(test => {
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
          isStaffOrSbcStaff: test.isStaffOrSbcStaff,
          userFirstName: test.userFirstName,
          userLastName: test.userLastName
        }
      })
    }
    )

    afterAll(() => {
      wrapper.destroy()
    })

    it(test.description, async () => {
      wrapper.setData({
        businessIdentifier: test.businessIdentifier,
        businessName: 'My Business Inc'
      })
      await flushPromises()

      // verify components
      expect(wrapper.attributes('id')).toBe('manage-business-dialog')
      expect(wrapper.find('#manage-business-dialog').isVisible()).toBe(true)
      // expect(wrapper.find('businesslookup-stub').exists()).toBe(true) // UN-COMMENT (see below)
      expect(wrapper.findComponent(HelpDialog).exists()).toBe(true)

      // button components
      expect(wrapper.find('#add-button span').text()).toBe('Manage This Business')
      expect(wrapper.find('#cancel-button span').text()).toBe('Cancel')
      if (!test.certifyExists) {
        expect(wrapper.find('#forgot-button').exists()).toBe(!!test.forgotButtonText)
      }
      if (test.forgotButtonText) {
        expect(wrapper.find('#forgot-button span').text()).toBe(test.forgotButtonText)
      }

      // *** UN-COMMENT THIS WHEN BUSINESS LOOKUP IS ENABLED ***
      // // verify data list
      // const dl = wrapper.find('dl')
      // const dt = dl.findAll('dt')
      // const dd = dl.findAll('dd')
      // expect(dt.at(0).text()).toBe('Business Name:')
      // expect(dd.at(0).text()).toBe('My Business Inc')
      // expect(dt.at(1).text()).toBe('Incorporation Number:')
      // expect(dd.at(1).text()).toBe(test.businessIdentifier)
      if (!test.isStaffOrSbcStaff) {
        expect(wrapper.find('.authorization').exists())
      }

      if (!test.isStaffOrSbcStaff) {
        expect(wrapper.find('.authorization').exists()).toBe(test.isStaffOrSbcStaff)
      }
    })
  })
})
