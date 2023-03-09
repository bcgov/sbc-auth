import { createLocalVue, mount } from '@vue/test-utils'
import InfoStepper from '@/components/auth/home/InfoStepper.vue'
import vueCompositionApi from '@vue/composition-api'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(vueCompositionApi)

document.body.setAttribute('data-app', 'true')

describe('InfoStepper.vue', () => {
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(vueCompositionApi)

    const vuetify = new Vuetify({})
    const router = new VueRouter()

    const store = new Vuex.Store({
      strict: false
    })

    wrapper = mount(InfoStepper, {
      store,
      router,
      localVue,
      vuetify,
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('is renders correctly', () => {
    expect(wrapper.find('.next-step-wrapper').exists()).toBe(true)
    expect(wrapper.find('#step-buttons-container').exists()).toBe(true)
    expect(wrapper.find('.next-step-btn').exists()).toBe(true)
    expect(wrapper.find('.step').exists()).toBe(true)
  })

  it('renders correct number of steps', () => {
    expect(wrapper.findAll('.step').length).toBe(4)
  })

//   it('is selects the 1st step initially', () => {
//     expect(wrapper.vm.currentStep).toBe(wrapper.vm.defaultSteps[0])
//   })

//   it('is gets step index correctly', () => {
//     const firstStep = wrapper.vm.defaultSteps[0]
//     expect(wrapper.vm.getStepIndex(firstStep)).toBe(1)
//   })

//   it('is step forwards correctly', () => {
//     expect(wrapper.vm.currentStepNumber).toBe(1)
//     wrapper.vm.stepForward()
//     expect(wrapper.vm.currentStepNumber).toBe(2)
//   })

//   it('is step backwards correctly', () => {
//     wrapper.vm.currentStepNumber = 3
//     wrapper.vm.stepBack()
//     expect(wrapper.vm.currentStepNumber).toBe(2)
//   })

//   it('is jumping to step correctly', () => {
//     wrapper.vm.jumpToStep(2)
//     expect(wrapper.vm.currentStepNumber).toBe(2)
//   })
})
