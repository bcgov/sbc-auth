import { createLocalVue, mount } from '@vue/test-utils'
import InfoStepper from '@/components/auth/home/InfoStepper.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import vueCompositionApi from '@vue/composition-api'

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
    localVue.use(VueRouter)

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
      mocks: {
        $route: {
          params: {
            id: 'id'
          }
        },
        $router: {
          params: {
            id: 'id'
          }
        }
      }
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

//     it('selects first step on render', async () => {
//       await wrapper.vm.$nextTick()
//       expect(wrapper.findAll('.step__label').at(0).classes()).toContain('selected')
//     })

//     it('steps forwards correctly', async () => {
//       await wrapper.find('#step-1-btn').trigger('click')
//       await wrapper.vm.$nextTick()
//       expect(wrapper.findAll('.step__label').at(0).classes()).toContain('selected')
//     })

//     it('jumping to last step correctly', async () => {
//       await wrapper.find('#step-4-btn').trigger('click')
//       await wrapper.vm.$nextTick()
//       expect(wrapper.find('.next-step-btn').classes()).toContain('hide-next-btn')
//       expect(wrapper.findAll('.step__label').at(3).classes()).toContain('selected')

//     })

//   it('jumping backwards correctly', async () => {
//     expect(wrapper.findAll('.step__label').at(0).classes()).toContain('selected')
//     await wrapper.find('#step-4-btn').trigger('click')
//     expect(wrapper.findAll('.step__label').at(3).classes()).toContain('selected')
//     await wrapper.find('#step-1-btn').trigger('click')
//     expect(wrapper.findAll('.step__label').at(0).classes()).toContain('selected')
//   })
})
