import { createLocalVue, mount } from '@vue/test-utils'
import { CorpTypes } from '@/util/constants'
import EntityManagement from '@/components/auth/manage-business/EntityManagement.vue'
import { RemoveBusinessPayload } from '@/models/Organization'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

function getPayLoad (type: any) {
  const removeNRPayload: RemoveBusinessPayload = {
    business: {
      corpType: {
        code: type as CorpTypes,
        desc: type as string
      },
      businessIdentifier: 'test',
      folioNumber: 'test'
    },
    orgIdentifier: 10
  }
  return removeNRPayload
}

describe('Entity Management Component', () => {
  let wrapper: any
  let mockedNrMethod: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    const $t = () => 'test'
    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
          name: 'new org',
          orgType: 'STAFF'
        }
      }
    }
    const businessModule = {
      namespaced: true,
      state: {
        businesses: []

      },
      action: {
        addBusiness: jest.fn(),
        updateBusinessName: jest.fn(),
        updateFolioNumber: jest.fn()
      }
    }

    const userModule: any = {
      namespaced: true,
      state: {
        currentUser: {
          firstName: 'Nadia',
          lastName: 'Woodie'
        }
      }
    }

    const store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule,
        business: businessModule,
        user: userModule
      }
    })
    wrapper = mount(EntityManagement, {
      vuetify,
      localVue,
      store,
      sync: false,
      mocks: { $t },
      computed: {
        enableBcCccUlc () {
          return true
        }
      }
    })
    mockedNrMethod = jest.fn()
    wrapper.vm.$refs.removalConfirmDialog.open = mockedNrMethod
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('EntityManagement is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('EntityManagement contains removalConfirmDialog modal', () => {
    const modal = wrapper.find({ ref: 'removalConfirmDialog' })
    expect(modal.exists()).toBe(true)
  })

  it('calls the nr open modal with correct buttons', async () => {
    const removeNRPayload = getPayLoad('NR')
    wrapper.vm.showConfirmationOptionsModal(removeNRPayload)
    expect(mockedNrMethod).toHaveBeenCalled()
    expect(wrapper.vm.primaryBtnText).toBe('Remove Name Request')
    expect(wrapper.vm.secondaryBtnText).toBe('Keep Name Request')
  })
  it('calls the IA open modal with correct buttons', async () => {
    const removeBusinessPayload: RemoveBusinessPayload = getPayLoad('TMP')
    wrapper.vm.showConfirmationOptionsModal(removeBusinessPayload)
    expect(mockedNrMethod).toHaveBeenCalled()
    expect(wrapper.vm.primaryBtnText).toBe('Delete Incorporation Application')
    expect(wrapper.vm.secondaryBtnText).toBe('Keep Incorporation Application')
  })
  it('calls the Passcode reset open modal with correct buttons', async () => {
    const removeBusinessPayload: RemoveBusinessPayload = getPayLoad('CP')
    const mockedPasscodeResetMethod = jest.fn()
    wrapper.vm.$refs.passcodeResetOptionsModal.open = mockedPasscodeResetMethod
    wrapper.vm.showConfirmationOptionsModal(removeBusinessPayload)
    expect(mockedNrMethod).toHaveBeenCalledTimes(0)
    expect(mockedPasscodeResetMethod).toHaveBeenCalled()
  })
  it('calls the IA open modal with correct buttons', async () => {
    const removeBusinessPayload: RemoveBusinessPayload = getPayLoad('SP')
    wrapper.vm.showConfirmationOptionsModal(removeBusinessPayload)
    expect(mockedNrMethod).toHaveBeenCalled()
    expect(wrapper.vm.primaryBtnText).toBe('Remove Registration')
    expect(wrapper.vm.secondaryBtnText).toBe('Keep Registration')
  })
  it('calls the IA open modal with correct buttons', async () => {
    const removeBusinessPayload: RemoveBusinessPayload = getPayLoad('GP')
    wrapper.vm.showConfirmationOptionsModal(removeBusinessPayload)
    expect(mockedNrMethod).toHaveBeenCalled()
    expect(wrapper.vm.primaryBtnText).toBe('Remove Registration')
    expect(wrapper.vm.secondaryBtnText).toBe('Keep Registration')
  })
  it('all buttons, tooltips and v-menu selections exist', async () => {
    // All buttons exist
    expect(wrapper.find('#add-existing-btn').exists()).toBe(true)
    expect(wrapper.find('#add-name-request-btn').exists()).toBe(true)
    expect(wrapper.find('#incorporate-numbered-btn').exists()).toBe(true)

    // Existing Business or NameRequest menu selections
    wrapper.find('#add-existing-btn').trigger('click')
    await Vue.nextTick()
    expect(wrapper.findAll('.add-existing-item').length).toBe(2)

    // tooltips exist
    expect(wrapper.findAll('.v-tooltip--top').length).toBe(2)
  })

  it('all incorporate numbered businesses btns exist', async () => {
    // Enter the Incorporate a Numbered BC Company drop down.
    const incorporateNumberedBtn = wrapper.find('#incorporate-numbered-btn')
    incorporateNumberedBtn.trigger('click')
    await Vue.nextTick()

    expect(wrapper.find('#incorporate-numbered-ben-btn').exists()).toBe(true)
    expect(wrapper.find('#incorporate-numbered-limited-btn').exists()).toBe(true)
    expect(wrapper.find('#incorporate-numbered-unlimited-btn').exists()).toBe(true)
    expect(wrapper.find('#incorporate-numbered-ccc-btn').exists()).toBe(true)
  })
})
