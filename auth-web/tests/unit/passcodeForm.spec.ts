import PasscodeForm from '@/components/PasscodeForm.vue'
import Vuex from 'vuex'
import { mount, createLocalVue } from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
Vue.use(Vuetify)
Vue.use(VueRouter)
describe('PasscodeForm.vue', () => {
  it('passcode screen', () => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      state: {
        entityNumber: '',
        passcode: ''
      }
    })

    const wrapper = mount(PasscodeForm, {
      store,
      localVue
    })

    expect(wrapper.find('.signinbtn').text().startsWith('Sign in')).toBeTruthy()
    expect(wrapper.isVueInstance()).toBeTruthy()
  })
})
