import { CorpTypes, SessionStorageKeys } from '@/util/constants'
import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import ManageBusinessDialog from '@/components/auth/manage-business/manage-business-dialog/ManageBusinessDialog.vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'

const vuetify = new Vuetify({})
const localVue = createLocalVue()

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
    userLastName: 'Woodie',
    businessLegalType: ''
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
    userLastName: 'Woodie',
    businessLegalType: ''
  },
  {
    description: 'Should render for a FM Client account',
    businessIdentifier: 'FM0000000',
    passcodeInputLabel: 'Proprietor or Partner Name (e.g., Last Name, First Name Middlename)',
    certifyExists: true,
    passcodeExists: true,
    folioNumberExists: true,
    isStaffOrSbcStaff: false,
    userFirstName: 'Nadia',
    userLastName: 'Woodie',
    businessLegalType: ''
  },
  {
    description: 'Should render for a FM Staff account',
    businessIdentifier: 'FM0000000',
    certifyExists: false,
    passcodeExists: false,
    folioNumberExists: false,
    isStaffOrSbcStaff: true,
    userFirstName: 'Nadia',
    userLastName: 'Woodie',
    businessLegalType: ''
  },
  {
    description: 'Should render for a FM SBC Staff account',
    businessIdentifier: 'FM0000000',
    certifyExists: false,
    passcodeExists: false,
    folioNumberExists: false,
    isStaffOrSbcStaff: true,
    userFirstName: 'Nadia',
    userLastName: 'Woodie',
    businessLegalType: ''
  },
  {
    description: 'Should render for a SP Entity',
    businessIdentifier: 'FM1018142',
    certifyExists: false,
    passcodeExists: false,
    folioNumberExists: false,
    isStaffOrSbcStaff: true,
    userFirstName: 'Nadia',
    userLastName: 'Woodie',
    businessLegalType: 'SP'
  },
  {
    description: 'Should render for a GP Entity',
    businessIdentifier: 'FM1000001',
    certifyExists: false,
    passcodeExists: false,
    folioNumberExists: false,
    isStaffOrSbcStaff: true,
    userFirstName: 'Nadia',
    userLastName: 'Woodie',
    businessLegalType: 'GP'
  },
  {
    description: 'Should render for a BC (Corporation) Entity',
    businessIdentifier: 'BC0111236',
    certifyExists: false,
    passcodeExists: false,
    folioNumberExists: false,
    isStaffOrSbcStaff: true,
    userFirstName: 'Nadia',
    userLastName: 'Woodie',
    businessLegalType: 'BC',
    hasBusinessAuthentication: true,
    hasBusinessEmail: true
  },
  {
    description: 'Should render for a BEN (Benefit Corporation) Entity',
    businessIdentifier: 'BC0871457',
    certifyExists: false,
    passcodeExists: false,
    folioNumberExists: false,
    isStaffOrSbcStaff: true,
    userFirstName: 'Nadia',
    userLastName: 'Woodie',
    businessLegalType: 'BEN',
    hasBusinessAuthentication: false,
    hasBusinessEmail: true
  },
  {
    description: 'Should render for a CP (Co-op) Entity',
    businessIdentifier: 'CP0000901',
    certifyExists: false,
    passcodeExists: false,
    folioNumberExists: false,
    isStaffOrSbcStaff: true,
    userFirstName: 'Nadia',
    userLastName: 'Woodie',
    businessLegalType: 'CP',
    hasBusinessAuthentication: true,
    hasBusinessEmail: false
  }
]

describe('ManageBusinessDialog grouped tests', () => {
  testCaseList.forEach(test => {
    let wrapper: Wrapper<any>

    beforeAll(() => {
      wrapper = shallowMount(ManageBusinessDialog, {
        localVue,
        vuetify,
        propsData: {
          isStaffOrSbcStaff: test.isStaffOrSbcStaff,
          userFirstName: test.userFirstName,
          userLastName: test.userLastName,
          businessLegalType: test.businessLegalType
        }
      })
    })

    afterAll(() => {
      wrapper.destroy()
    })

    it(test.description, async () => {
      const isBusinessLegalTypeCorporation = test.businessLegalType === CorpTypes.BC_COMPANY
      const isBusinessLegalTypeBenefit = test.businessLegalType === CorpTypes.BENEFIT_COMPANY
      const isBusinessLegalTypeCoOp = test.businessLegalType === CorpTypes.COOP
      const isBusinessLegalTypeSoleProprietorship = test.businessLegalType === CorpTypes.SOLE_PROP
      const isBusinessLegalTypePartnership = test.businessLegalType === CorpTypes.PARTNERSHIP
      const isBusinessLegalTypeFirm = isBusinessLegalTypeSoleProprietorship || isBusinessLegalTypePartnership

      wrapper.setData({
        businessIdentifier: test.businessIdentifier,
        businessName: 'My Business Inc',
        hasBusinessAuthentication: test.hasBusinessAuthentication,
        hasBusinessEmail: test.hasBusinessEmail
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
        expect(wrapper.find('.authorization').exists()).toBe(test.isStaffOrSbcStaff)
      }
      if (isBusinessLegalTypeCorporation || isBusinessLegalTypeBenefit || isBusinessLegalTypeCoOp) {
        if (test.hasBusinessAuthentication && test.hasBusinessEmail) {
          expect(wrapper.find('#manage-business-dialog-passcode-group').exists())
          expect(wrapper.find('#manage-business-dialog-passcode-group').isVisible()).toBe(true)
        } else {
          expect(wrapper.find('#manage-business-dialog-passcode-group').exists()).toBeFalsy()
        }
      } else if (isBusinessLegalTypeFirm) {
        expect(wrapper.find('#manage-business-dialog-proprietor-partner-name-group').exists())
        expect(wrapper.find('#manage-business-dialog-proprietor-partner-name-group').isVisible()).toBe(true)
        expect(wrapper.find('#manage-business-dialog-passcode-group').exists()).toBeFalsy()
      } else {
        expect(wrapper.find('#manage-business-dialog-proprietor-partner-name-group').exists()).toBeFalsy()
        expect(wrapper.find('#manage-business-dialog-email-group').exists()).toBeFalsy()
        expect(wrapper.find('#manage-business-dialog-passcode-group').exists()).toBeFalsy()
      }
    })
  })
})

describe('ManageBusinessDialog Component', () => {
  let wrapper: Wrapper<any>

  beforeAll(() => {
    wrapper = shallowMount(ManageBusinessDialog, {
      vuetify,
      propsData: {
        userFirstName: 'Nadia',
        userLastName: 'Woodie'
      }
    })
  })

  afterAll(() => {
    wrapper.destroy()
  })

  it('Should compute the correct boolean for isDialogVisible()', async () => {
    await wrapper.setProps({ showBusinessDialog: true })
    expect(wrapper.vm.isDialogVisible).toBe(true)
    await wrapper.setProps({ showBusinessDialog: false })
    expect(wrapper.vm.isDialogVisible).toBe(false)
  })

  it('Should compute the correct boolean for isBusinessLegalTypeFirm()', async () => {
    await wrapper.setProps({ businessLegalType: CorpTypes.SOLE_PROP })
    expect(wrapper.vm.isBusinessLegalTypeFirm).toBe(true)
    await wrapper.setProps({ businessLegalType: CorpTypes.PARTNERSHIP })
    expect(wrapper.vm.isBusinessLegalTypeFirm).toBe(true)
    await wrapper.setProps({ businessLegalType: CorpTypes.COOP })
    expect(wrapper.vm.isBusinessLegalTypeFirm).toBe(false)
  })

  it('Should compute the correct boolean for isBusinessLegalTypeCorporation()', async () => {
    await wrapper.setProps({ businessLegalType: CorpTypes.BC_COMPANY })
    expect(wrapper.vm.isBusinessLegalTypeCorporation).toBe(true)
    await wrapper.setProps({ businessLegalType: CorpTypes.SOLE_PROP })
    expect(wrapper.vm.isBusinessLegalTypeCorporation).toBe(false)
  })

  it('Should compute the correct boolean for isBusinessLegalTypeBenefit()', async () => {
    await wrapper.setProps({ businessLegalType: CorpTypes.BENEFIT_COMPANY })
    expect(wrapper.vm.isBusinessLegalTypeBenefit).toBe(true)
    await wrapper.setProps({ businessLegalType: CorpTypes.SOLE_PROP })
    expect(wrapper.vm.isBusinessLegalTypeCorporation).toBe(false)
  })

  it('Should compute the correct boolean for isBusinessLegalTypeCoOp()', async () => {
    await wrapper.setProps({ businessLegalType: CorpTypes.COOP })
    expect(wrapper.vm.isBusinessLegalTypeCoOp).toBe(true)
    await wrapper.setProps({ businessLegalType: CorpTypes.SOLE_PROP })
    expect(wrapper.vm.isBusinessLegalTypeCorporation).toBe(false)
  })

  it('Should compute the correct boolean for showAuthorization()', async () => {
    await wrapper.setProps({ businessLegalType: CorpTypes.SOLE_PROP })
    await wrapper.setProps({ isStaffOrSbcStaff: true })
    expect(wrapper.vm.showAuthorization).toBe(true)
    await wrapper.setProps({ isStaffOrSbcStaff: false })
    expect(wrapper.vm.showAuthorization).toBe(false)
    await wrapper.setProps({ businessLegalType: CorpTypes.COOP })
    await wrapper.setProps({ isStaffOrSbcStaff: true })
    expect(wrapper.vm.showAuthorization).toBe(false)
  })

  it('Should compute the correct value for passcodeLabel(), passcodeHint() and passcodeMaxLength()', async () => {
    await wrapper.setProps({ businessLegalType: CorpTypes.SOLE_PROP })
    expect(wrapper.vm.passcodeLabel).toBe('Proprietor or Partner Name (e.g., Last Name, First Name Middlename)')
    expect(wrapper.vm.passcodeHint).toBe('Name as it appears on the Business Summary or the Statement of Registration')
    expect(wrapper.vm.passcodeMaxLength).toBe(150)
    await wrapper.setProps({ businessLegalType: undefined })
    expect(wrapper.vm.passcodeLabel).toBe('Password')
    expect(wrapper.vm.passcodeHint).toBe('Password must be 8 to 15 characters')
    expect(wrapper.vm.passcodeMaxLength).toBe(15)
  })

  it('Should compute the correct value for certifiedBy()', async () => {
    await wrapper.setProps({ isStaffOrSbcStaff: false })
    expect(wrapper.vm.certifiedBy).toBe('Woodie, Nadia')
  })

  it('showPasscodeOption shows correct business types by default', async () => {
    // Defaults for no connection to LD.
    wrapper.vm.hasBusinessAuthentication = true
    await wrapper.setProps({ businessLegalType: CorpTypes.BC_COMPANY })
    expect(wrapper.vm.showPasscodeOption).toBe(true)
    await wrapper.setProps({ businessLegalType: CorpTypes.PARTNERSHIP })
    expect(wrapper.vm.showPasscodeOption).toBe(true)
    await wrapper.setProps({ businessLegalType: CorpTypes.SOLE_PROP })
    expect(wrapper.vm.showPasscodeOption).toBe(true)
    await wrapper.setProps({ businessLegalType: CorpTypes.BENEFIT_COMPANY })
    expect(wrapper.vm.showPasscodeOption).toBe(false)
    await wrapper.setProps({ businessLegalType: CorpTypes.COOP })
    expect(wrapper.vm.showPasscodeOption).toBe(false)

    // Launch darkly flags, show for all
    sessionStorage[SessionStorageKeys.LaunchDarklyFlags] = JSON.stringify({ 'allowable-business-passcode-types': 'CP' })
    wrapper = shallowMount(ManageBusinessDialog, {
      vuetify,
      propsData: {
        userFirstName: 'Nadia',
        userLastName: 'Woodie'
      }
    })
    wrapper.vm.hasBusinessAuthentication = true
    await wrapper.setProps({ businessLegalType: CorpTypes.COOP })
    expect(wrapper.vm.showPasscodeOption).toBe(true)
    await wrapper.setProps({ businessLegalType: CorpTypes.BENEFIT_COMPANY })
    expect(wrapper.vm.showPasscodeOption).toBe(false)
  })
})
