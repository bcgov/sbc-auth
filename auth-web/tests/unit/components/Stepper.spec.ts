import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import Stepper from '@/components/auth/common/stepper/Stepper.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('Stepper.vue', () => {
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const vuetify = new Vuetify({})

    const store = new Vuex.Store({
      strict: false
    })

    wrapper = mount(Stepper, {
      store,
      localVue,
      vuetify
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('is default configurations are correct', () => {
    expect(wrapper.vm.defaultSteps.length).toBe(3)
  })

  it('is renders correctly', () => {
    expect(wrapper.find('.stepper')).toBeTruthy()
    expect(wrapper.find('.stepper-nav')).toBeTruthy()
    expect(wrapper.find('.stepper-content')).toBeTruthy()
  })

  it('is renders correct number of steps', () => {
    expect(wrapper.findAll('.stepper-nav .v-stepper__step').length).toBe(wrapper.vm.defaultSteps.length)
  })

  it('is selects the 1st step initially', () => {
    expect(wrapper.vm.currentStep).toBe(wrapper.vm.defaultSteps[0])
  })

  it('is gets step title and name correctly', () => {
    const firstStep = wrapper.vm.defaultSteps[0]
    expect(wrapper.vm.getStepTitle(firstStep)).toBe(firstStep.title)
    expect(wrapper.vm.getStepName(firstStep)).toBe(firstStep.stepName)
  })

  it('is gets step props', () => {
    const firstStep = wrapper.vm.defaultSteps[0]
    const stepProp = {
      stepForward: jest.fn(),
      stepBack: jest.fn(),
      jumpToStep: jest.fn()
    }
    const props = Object.keys(wrapper.vm.getPropsForStep(firstStep))
    expect(props.length).toBe(Object.keys(stepProp).length)
  })

  it('is gets step index correctly', () => {
    const firstStep = wrapper.vm.defaultSteps[0]
    expect(wrapper.vm.getStepIndex(firstStep)).toBe(1)
  })

  it('is step forwards correctly', () => {
    expect(wrapper.vm.currentStepNumber).toBe(1)
    wrapper.vm.stepForward()
    expect(wrapper.vm.currentStepNumber).toBe(2)
  })

  it('is step backwards correctly', () => {
    wrapper.vm.currentStepNumber = 3
    wrapper.vm.stepBack()
    expect(wrapper.vm.currentStepNumber).toBe(2)
  })

  it('is jumping to step correctly', () => {
    wrapper.vm.jumpToStep(2)
    expect(wrapper.vm.currentStepNumber).toBe(2)
  })
})
