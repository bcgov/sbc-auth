import { createLocalVue, shallowMount } from '@vue/test-utils'
import AddBusinessDialog from '@/components/auth/manage-business/AddBusinessDialog.vue'
import AffiliatedEntityTable from '@/components/auth/manage-business/AffiliatedEntityTable.vue'
import DashboardHelp from '@/components/auth/manage-business/DashboardHelp.vue'
import EntityManagement from '@/components/auth/manage-business/EntityManagement.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PasscodeResetOptionsModal from '@/components/auth/manage-business/PasscodeResetOptionsModal.vue'
import { RemoveBusinessPayload } from '@/models/Organization'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

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
    wrapper = shallowMount(EntityManagement, {
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
    expect(wrapper.vm).toBeTruthy()
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

  it('renders the EntityManagement component and default subcomponents', () => {
    expect(wrapper.find(EntityManagement).exists()).toBe(true)
    expect(wrapper.find(AffiliatedEntityTable).exists()).toBe(true)
    expect(wrapper.find(PasscodeResetOptionsModal).exists()).toBe(true)
    expect(wrapper.find(AddBusinessDialog).exists()).toBe(true)
    expect(wrapper.find(ModalDialog).exists()).toBe(true)
    expect(wrapper.find(DashboardHelp).exists()).toBe(true)
  })
})
