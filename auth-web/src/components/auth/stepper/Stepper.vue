<template>
  <v-stepper v-model="currentStepNumber">
    <v-row>
      <v-col class="stepper-menu" :cols="2">
        <v-stepper-step
          v-for="step in steps"
          :key="getStepIndex(step)"
          :complete="currentStepNumber > getStepIndex(step)"
          :step="getStepIndex(step)"
        >{{ step.title }}</v-stepper-step>
      </v-col>
      <v-divider vertical />
      <v-col>
        <div v-for="step in steps" :key="step.title" class="flex-grow">
          <component
            class="pa-2"
            v-if="getStepIndex(step) === currentStepNumber"
            :is="step.component"
            v-bind="getPropsForStep(step)"
            keep-alive
            transition="fade"
            mode="out-in"
          />
        </div>
      </v-col>
    </v-row>
  </v-stepper>
</template>

<script lang="ts">
import { Component, Prop } from 'vue-property-decorator'
import StepperStub from '@/components/auth/stepper/StepperStub.vue'
import Vue from 'vue'

export interface StepConfiguration {
  title: string
  component: Vue.Component
  componentProps: Record<string, any>
}

@Component({
  name: 'Stepper',
  components: {
    StepperStub
  }
})
export default class Stepper extends Vue {
  @Prop({ default: null }) stepperConfiguration!: StepConfiguration[]
  private steps: StepConfiguration[]
  private currentStepNumber = 1

  private get defaultSteps (): Array<StepConfiguration> {
    return [
      {
        title: 'Step 1',
        component: StepperStub,
        componentProps: {}
      },
      {
        title: 'Step 2',
        component: StepperStub,
        componentProps: {}
      },
      {
        title: 'Step 3',
        component: StepperStub,
        componentProps: {}
      }
    ]
  }

  private get currentStep (): StepConfiguration {
    return this.steps.find(step => this.getStepIndex(step) === this.currentStepNumber)
  }

  private getPropsForStep (step: StepConfiguration): Record<string, any> {
    return { ...step.componentProps, stepForward: this.stepForward, stepBack: this.stepBack }
  }

  private getStepIndex (step: StepConfiguration): number {
    return this.steps.indexOf(step) + 1
  }

  private stepForward () {
    if (this.currentStepNumber >= this.steps.length) {
      // TODO, decide where to route to after account creation is done
    } else {
      this.currentStepNumber++
    }
  }

  private stepBack () {
    this.currentStepNumber = Math.max(1, this.currentStepNumber - 1)
  }

  private async beforeMount () {
    this.steps = this.stepperConfiguration || this.defaultSteps
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  .stepper-menu {
    min-width: 25%;
  }
</style>
