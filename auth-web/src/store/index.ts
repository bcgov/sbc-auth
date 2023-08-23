import { PiniaVuePlugin, createPinia } from 'pinia'
import Vue from 'vue'

/**
 * Configures and returns Pinia Store.
 */
export function getPiniaStore () {
  Vue.use(PiniaVuePlugin)

  return createPinia()
}

export * from './activityLog'
export * from './business'
export * from './codes'
export * from './org'
export * from './staff'
export * from './task'
export * from './user'
