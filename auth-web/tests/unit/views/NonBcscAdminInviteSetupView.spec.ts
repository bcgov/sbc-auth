import { createLocalVue, shallowMount } from '@vue/test-utils'
import NonBcscAdminInviteSetupView from '@/views/auth/create-account/non-bcsc/NonBcscAdminInviteSetupView.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import { useUserStore } from '@/store/user'

const vuetify = new Vuetify({})
const router = new VueRouter()

describe('NonBcscAdminInviteSetupView.vue', () => {
  let wrapper: any
  beforeEach(() => {
    const localVue = createLocalVue()
    const userStore = useUserStore()
    userStore.userProfile = {} as any
    userStore.createAffidavit = vi.fn()
    wrapper = shallowMount(NonBcscAdminInviteSetupView, {
      localVue,
      router,
      vuetify
    })
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('update current step properly', async () => {
    wrapper.vm.goToNextStep()
    expect(wrapper.vm.currentStep).toEqual(2)
    wrapper.vm.goBackPreviousStep()
    expect(wrapper.vm.currentStep).toEqual(1)
  })
})
