import { createLocalVue, mount } from '@vue/test-utils'
import LoginBCSC from '@/components/auth/home/LoginBCSC.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

document.body.setAttribute('data-app', 'true')

describe('LoginBCSC.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)

    const router = new VueRouter()
    const vuetify = new Vuetify({})

    wrapperFactory = (slotsData) => {
      return mount(LoginBCSC, {
        router,
        vuetify,
        localVue,
        slots: {
          ...slotsData
        }
      })
    }

    wrapper = wrapperFactory({})
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('it renders correctly with default slot', () => {
    expect(wrapper.find('.v-card__title').text()).toBe('Create a BC Registries Account')
    expect(wrapper.find('.font-weight-bold').text()).toBe('Log in')
  })

  it('it renders slot', () => {
    wrapper = wrapperFactory({ actions: '<div>Action</div>' })
    expect(wrapper.html()).toContain('<div>Action</div>')
  })
})
