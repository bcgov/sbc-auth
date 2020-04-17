<template>
  <v-card flat>
    <v-card-title>Component Title</v-card-title>
    <v-card-text>
      <p>Component Content</p>
      <v-card-actions>
        <v-btn @click="back()">Back</v-btn>
        <v-btn @click="next()">Next Step</v-btn>
      </v-card-actions>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
@Component({
  name: 'StepperStub'
})
export default class StepperStub extends Vue {
  @Prop() stepForward!: () => void
  @Prop() stepBack!: () => void

  private next () {
    this.stepForward()
  }

  private back () {
    this.stepBack()
  }
}
</script>

<style lang="scss" scoped>
</style>
