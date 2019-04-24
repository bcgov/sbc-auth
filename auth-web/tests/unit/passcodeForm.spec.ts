import PasscodeForm from '@/components/PasscodeForm.vue'
import Vuex from 'vuex'
import { mount, createLocalVue } from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
Vue.use(Vuetify)
Vue.use(VueRouter)
describe('PasscodeForm.vue', () => {
  let cmp

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      state: {
        entityNumber: '',
        passcode: ''

      },
      getters: {
        entityNumber: (state) => state.entityNumber,
        passcode: (state) => state.passcode
      },
      mutations: {
        entityNumber (state, entityNumber) {
          state.entityNumber = entityNumber
        },

        passcode (state, passcode) {
          state.passcode = passcode
        }
      }
    })

    cmp = mount(PasscodeForm, {
      store,
      localVue
    })
  })

  it('passcode screen login button exists', () => {
    expect(cmp.find('.sign-in-btn').text().startsWith('Sign in')).toBeTruthy()
    expect(cmp.isVueInstance()).toBeTruthy()
  })

  it('passcode and entity number is empty', () => {
    expect(cmp.vm.entityNumber).toBe('')
    expect(cmp.vm.passcode).toBe('')
  })

  it('passcode and entity number is the values in store', () => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      state: {
        entityNumber: 'somenumber',
        passcode: 'somevalue'
      }
    })

    cmp = mount(PasscodeForm, {
      store,
      localVue
    })

    cmp.vm.$refs.form.validate()

    expect(cmp.vm.entityNumber).toBe('somenumber')
    expect(cmp.vm.passcode).toBe('somevalue')
  })
})
