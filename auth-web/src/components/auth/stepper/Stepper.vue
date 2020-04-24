<template>
  <v-stepper v-model="currentStepNumber">
    <v-row class="mx-0">
      <v-col class="stepper-menu" :cols="2">
        <v-stepper-step
          v-for="step in steps"
          :key="getStepIndex(step)"
          :complete="currentStepNumber > getStepIndex(step)"
          :step="getStepIndex(step)"
        >{{ getStepTitle(step) }}</v-stepper-step>
      </v-col>
      <v-col class="pa-9">
        <div v-for="step in steps" :key="getStepIndex(step)" class="flex-grow">
          <template v-if="getStepIndex(step) === currentStepNumber">
            <div class="stepper-count mb-1">Step {{currentStepNumber}} of {{steps.length}}</div>
            <h2 class="mb-4">{{getStepTitle(step)}}</h2>
            <component
              class="pa-0"
              :is="currentStep.component"
              v-bind="getPropsForStep(step)"
              keep-alive
              transition="fade"
              mode="out-in"
            />
          </template>
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
  alternate?: StepConfiguration // Steps can have an alternate configuration which can be used when invoking stepForward
}

@Component({
  name: 'Stepper',
  components: {
    StepperStub
  }
})
export default class Stepper extends Vue {
  @Prop({ default: null }) stepperConfiguration!: StepConfiguration[]
  @Prop({ default: '/business' }) redirectWhenDone!: string
  private steps: StepConfiguration[]
  private currentStepNumber = 1
  private useAlternateStep = false

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
    const current = this.steps.find(step => this.getStepIndex(step) === this.currentStepNumber)
    return this.useAlternateStep ? current.alternate : current
  }

  private getStepTitle (step: StepConfiguration) {
    return this.useAlternateStep && this.currentStepNumber === this.getStepIndex(step) ? step.alternate?.title : step.title
  }

  private getPropsForStep (step: StepConfiguration): Record<string, any> {
    return { ...step.componentProps, stepForward: this.stepForward, stepBack: this.stepBack, jumpToStep: this.jumpToStep }
  }

  private getStepIndex (step: StepConfiguration): number {
    return this.steps.indexOf(step) + 1
  }

  private stepForward (useAlternateStep = false) {
    if (this.currentStepNumber >= this.steps.length) {
      this.$router.push(this.redirectWhenDone)
    } else {
      this.useAlternateStep = useAlternateStep && !!this.steps[this.currentStepNumber].alternate
      this.currentStepNumber++
    }
  }

  private stepBack () {
    this.useAlternateStep = false
    this.currentStepNumber = Math.max(1, this.currentStepNumber - 1)
  }

  private jumpToStep (index: number, useAlternateStep = false) {
    if (index > 0 && index <= this.steps.length) {
      this.useAlternateStep = useAlternateStep && !!this.steps[index].alternate
      this.currentStepNumber = index
    }
  }

  private async beforeMount () {
    this.steps = this.stepperConfiguration || this.defaultSteps
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  .stepper-menu {
    min-width: 24%;
  }
  .stepper-count {
    font-weight: 600;
    font-size: 1.05rem;
    text-transform: uppercase;
    color: $gray6;
  }
</style>
