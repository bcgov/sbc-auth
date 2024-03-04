import { createLocalVue, mount } from '@vue/test-utils'
import ChooseAuthMethodView from '@/views/auth/ChooseAuthMethodView.vue'
import { LoginSource } from '@/util/constants'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

document.body.setAttribute('data-app', true)

describe('ChooseAuthMethodView.vue', () => {
  let wrapper

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    localVue.use(Vuex)

    const router = new VueRouter()
    const vuetify = new Vuetify({})

    const store = new Vuex.Store({
      state: {},
      getters: {
        isAuthenticated: () => false
      }
    })

    wrapper = mount(ChooseAuthMethodView, {
      localVue,
      router,
      vuetify,
      store,
      mocks: {
        $t: (mock) => mock
      }
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

  it('displays the BC Service Card login button and triggers goNext with LoginSource.BCSC on click', async () => {
    expect(wrapper.find('#bcsc-login').exists()).toBe(true)
    const goNextBCSCSpy = vi.spyOn(wrapper.vm, 'goNext')
    await wrapper.find('#bcsc-login').trigger('click')
    expect(goNextBCSCSpy).toHaveBeenCalledWith(LoginSource.BCSC)
  })

  it('displays the BCeID login button and triggers goNext with LoginSource.BCEID on click', async () => {
    await wrapper.setData({ showBCeIDOption: true })
    await wrapper.vm.$nextTick()

    expect(wrapper.find('#bceid-login').exists()).toBe(true)
    const goNextBCeidSpy = vi.spyOn(wrapper.vm, 'goNext')
    await wrapper.find('#bceid-login').trigger('click')
    expect(goNextBCeidSpy).toHaveBeenCalledWith(LoginSource.BCEID)
  })
})
