import { createLocalVue, mount } from '@vue/test-utils'
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

function getPayLoad (type:string) {
  const removeNRPayload: RemoveBusinessPayload = {
    business: {
      corpType: {
        code: type,
        desc: type
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
          name: 'new org'
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

    const store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule,
        business: businessModule
      }
    })
    wrapper = mount(EntityManagement, {
      vuetify,
      localVue,
      store,
      sync: false,
      mocks: { $t }
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
    expect(wrapper.findAll('.top-tooltip').length).toBe(2)
  })
})
