<template>
  <v-card flat>
    <v-card-title>Component Title</v-card-title>
    <v-card-text>
      <p>Component Content</p>
      <v-card-actions>
        <v-btn @click="back()">Back</v-btn>
        <v-btn @click="next()">Next Step</v-btn>
        <v-btn @click="nextWithAlternate()">Next Step with Variant</v-btn>
        <v-btn @click="jumpToLast()">Jump to Last Step</v-btn>
      </v-card-actions>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { Component, Mixins } from 'vue-property-decorator'

@Component({
  name: 'StepperStub'
})
export default class StepperStub extends Mixins(Steppable) {
  private next () {
    this.stepForward()
  }

  private nextWithAlternate () {
    this.stepForward(true)
  }

  private back () {
    this.stepBack()
  }

  private jumpToLast () {
    this.jumpToStep(3)
  }
}
</script>
