<template>
  <v-stepper class="stepper d-flex" v-model="currentStepNumber">
    <v-container class="stepper-nav py-7 pl-8" :cols="2">
      <template v-for="step in steps">
        <v-stepper-step
          class="pa-3"
          :key="getStepIndex(step)"
          :complete="currentStepNumber > getStepIndex(step)"
          :step="getStepIndex(step)"
        >{{ getStepTitle(step) }}</v-stepper-step>
        <v-divider vertical :key="step" v-if="step !== steps"></v-divider>
      </template>
    </v-container>
    <v-container class="stepper-content pa-9">
      <div v-for="step in steps" :key="getStepIndex(step)" class="flex-grow">
        <template v-if="getStepIndex(step) === currentStepNumber">
          <div class="stepper-content__count mt-1 mb-1">Step {{currentStepNumber}} of {{steps.length}}</div>
          <h2 class="stepper-content__title mb-6">{{getStepTitle(step)}}</h2>
          <component
            class="pa-0"
            :is="currentStep.component"
            v-bind="getPropsForStep(step)"
            keep-alive
          />
        </template>
      </div>
    </v-container>
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

  .stepper-nav {
    width: 18rem;
    flex: 0 0 auto;

    hr:last-child {
      display: none;
    }
  }

  .stepper-content {
    flex: 1 1 auto;

    &__count {
      color: var(--v-grey-darken1);
      text-transform: uppercase;
      font-size: 0.9375rem;
      font-weight: bold;
    }

    &__title {
      font-size: 1.5rem;
    }
  }

  // Stepper
   $step-icon-size: 1.8rem;
   $step-font-size: 0.8375rem;

  .v-stepper {
    box-shadow: none;
    overflow: visible;

    .v-divider {
      margin-left: 1.65rem;
      height: 1.5rem;
      min-height: 1.5rem;
      max-height: 1.5rem;
      border-width: 1px;
    }
  }

  .v-stepper__step {
    border-radius: 4px;
    font-size: $step-font-size;
    font-weight: 700;

    ::v-deep {
      .v-stepper__step__step {
        margin-right: 1rem;
        width: $step-icon-size;
        height: $step-icon-size;
        min-width: $step-icon-size
      }
    }
  }

  .v-stepper__step:focus,
  .v-stepper__step:active {
    outline: none;
    box-shadow: 0 0 0 1px var(--v-primary-base);
  }

  .v-stepper__step:hover,
  .v-stepper__step--active {
    ::v-deep {
      .v-stepper__label {
        text-shadow: none !important;
        color: var(--v-primary-base) !important;
      }
    }
  }

  .v-stepper__step--complete {
    ::v-deep {
      .v-stepper__step__step {
        border: 2px solid var(--v-primary-base) !important;
        background-color: transparent !important;
      }
      .v-icon {
        color: var(--v-primary-base) !important;
      }
    }
  }

  .theme--light.v-stepper .v-stepper__step--complete .v-stepper__label {
    color: rgba(0,0,0,.38);
  }

  ::v-deep {
    .step-btns .v-btn {
      width: 7rem;
      font-weight: 700;
    }
  }

  .fade-enter-active,
  .fade-leave-active {
    transition-duration: 0.3s;
    transition-property: opacity;
    transition-timing-function: ease;
  }

  .fade-enter,
  .fade-leave-active {
    opacity: 0
  }
</style>
