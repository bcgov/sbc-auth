<template>
  <v-stepper
    v-model="currentStepNumber"
    class="stepper d-flex elevation-0"
    data-test="div-account-setup-stepper"
  >
    <v-container
      class="stepper-nav pa-10 pr-0"
      :class="stepperColor"
    >
      <template v-for="step in steps">
        <v-stepper-step
          :key="`${getStepIndex(step)}-step`"
          class="pa-3"
          :complete="currentStepNumber > getStepIndex(step)"
          :step="getStepIndex(step)"
          :data-test="`${getStepIndex(step)}-step`"
        >
          {{ getStepName(step) }}
        </v-stepper-step>
        <v-divider
          v-if="step !== steps"
          :key="`${getStepIndex(step)}-divider`"
          vertical
          class="step-divider mt-n1 mb-n1"
        />
      </template>
    </v-container>
    <v-divider
      vertical
      class="my-10"
    />
    <v-container class="stepper-content pa-12">
      <v-fade-transition>
        <div
          v-if="isLoading"
          class="loading-container"
        >
          <v-progress-circular
            size="50"
            width="5"
            color="primary"
            :indeterminate="isLoading"
          />
        </div>
      </v-fade-transition>
      <div
        v-for="step in steps"
        :key="getStepIndex(step)"
        class="flex-grow"
      >
        <template v-if="getStepIndex(step) === currentStepNumber">
          <div class="stepper-content__count mb-1 text--secondary">
            Step {{ currentStepNumber }} of {{ steps.length }}
          </div>
          <h2 class="stepper-content__title mb-3">
            {{ getStepTitle(step) }}
          </h2>
          <component
            :is="currentStep.component"
            class="pa-0"
            v-bind="getPropsForStep(step)"
            keep-alive
            @final-step-action="emitFinalStepAction"
          />
        </template>
      </div>
    </v-container>
  </v-stepper>
</template>

<script lang="ts">
import { Component, Emit, Prop } from 'vue-property-decorator'
import StepperStub from '@/components/auth/common/stepper/StepperStub.vue'
import Vue from 'vue'

export interface StepConfiguration {
  title: string
  stepName: string
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
  @Prop({ default: false }) isLoading!: boolean
  @Prop({ default: '' }) stepperColor!: string
  steps: StepConfiguration[]
  currentStepNumber = 1
  useAlternateStep = false

  get defaultSteps (): Array<StepConfiguration> {
    return [
      {
        title: 'Step 1',
        stepName: 'Step Name 1',
        component: StepperStub,
        componentProps: {}
      },
      {
        title: 'Step 2',
        stepName: 'Step Name 2',
        component: StepperStub,
        componentProps: {}
      },
      {
        title: 'Step 3',
        stepName: 'Step Name 3',
        component: StepperStub,
        componentProps: {}
      }
    ]
  }

  get currentStep (): StepConfiguration {
    const current = this.steps.find(step => this.getStepIndex(step) === this.currentStepNumber)
    return this.useAlternateStep ? current.alternate : current
  }

  getStepTitle (step: StepConfiguration) {
    return this.useAlternateStep && this.currentStepNumber === this.getStepIndex(step) ? step.alternate?.title : step.title
  }

  getStepName (step: StepConfiguration) {
    return this.useAlternateStep && this.currentStepNumber === this.getStepIndex(step) ? step.alternate?.stepName : step.stepName
  }

  getPropsForStep (step: StepConfiguration): Record<string, any> {
    return { ...step.componentProps, stepForward: this.stepForward, stepBack: this.stepBack, jumpToStep: this.jumpToStep }
  }

  getStepIndex (step: StepConfiguration): number {
    return this.steps.indexOf(step) + 1
  }

  stepForward (useAlternateStep = false) {
    if (this.currentStepNumber >= this.steps.length) {
      this.$router.push(this.redirectWhenDone)
    } else {
      this.useAlternateStep = useAlternateStep && !!this.steps[this.currentStepNumber].alternate
      this.currentStepNumber++
    }
  }

  stepBack (useAlternateStep = false) {
    this.currentStepNumber = Math.max(1, this.currentStepNumber - 1)
    this.useAlternateStep = useAlternateStep && !!this.steps[this.currentStepNumber - 1].alternate
  }

  jumpToStep (index: number, useAlternateStep = false) {
    if (index > 0 && index <= this.steps.length) {
      this.useAlternateStep = useAlternateStep && !!this.steps[index].alternate
      this.currentStepNumber = index
    }
  }

  private async beforeMount () {
    this.steps = this.stepperConfiguration || this.defaultSteps
  }

  @Emit('final-step-action')
  emitFinalStepAction (stepperData) {
    return stepperData
  }
}
</script>

<style lang="scss" scoped>
  // Stepper Navigation
  $step-font-size: 0.875rem;
  $step-icon-size: 2rem;
  $step-divider-height: 2rem;

  .v-stepper {
    box-shadow: none;
    overflow: visible;

    .step-divider {
      margin-left: 1.7rem;
      height: $step-divider-height;
      min-height: $step-divider-height;
      max-height: $step-divider-height;
    }
  }

  @media (max-width: 1024px) {
    .stepper-nav,
    .stepper-nav + hr {
      display: none;
    }
  }

  .v-stepper__step {
    border-radius: 4px;
    pointer-events: none;
    opacity: 0.5;
    font-weight: 700;
    transition: all ease-out 0.5s;

    + .v-divider {
      opacity: 0.5;
    }

    ::v-deep {
      .v-stepper__step__step {
        margin-right: 1rem;
        width: $step-icon-size;
        height: $step-icon-size;
        min-width: $step-icon-size;
      }

      .v-stepper__label {
        font-size: $step-font-size;
        text-shadow: none !important;
      }
    }
  }

  .v-stepper__step:focus,
  .v-stepper__step:active {
    outline: none;

    .v-stepper__label {
      text-shadow: none !important;
      color: var(--v-primary-base) !important;
    }
  }

  .v-stepper__step:hover,
  .v-stepper__step--active {
    opacity: 1;

    ::v-deep {
      .v-stepper__label {
        text-shadow: none !important;
        color: var(--v-primary-base) !important;
      }
    }
  }

  .v-stepper__step--complete {
    opacity: 1;

    .v-stepper__label {
      opacity: 0.5;
    }

    + .v-divider {
      border-color: var(--v-primary-base) !important;
      opacity: 1;
    }
  }

  .stepper-nav {
    flex: 0 0 auto;
    width: 20rem;
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;

    hr:last-child {
      display: none;
    }
  }

  // Primary Stepper
  $stepper-primary-color: var(--v-primary-base) !important;
  $stepper-primary-font-color: #ffffff !important;
  $stepper-primary-divider-height: 2rem;
  $stepper-primary-divider-color: #ffffff !important;

  .stepper-nav.primary {
    background-color: $stepper-primary-color;

    .v-stepper__step {
      + .v-divider {
        border-color: $stepper-primary-divider-color;
      }

      ::v-deep {
        .v-stepper__step__step {
          color: $stepper-primary-color;
          background-color: $stepper-primary-font-color;
        }

        .v-stepper__label {
          color: $stepper-primary-font-color;
        }
      }

      &:hover,
      &--active,
      &--complete {
        color: $stepper-primary-color;
      }
    }

    .v-stepper__step--complete {
      ::v-deep {
        .v-stepper__step__step {

          .v-icon {
            color: $stepper-primary-color;
          }
        }
      }
    }
  }

  // Error Stepper
  $stepper-error-color: var(--v-error-base) !important;
  $stepper-error-font-color: #ffffff !important;
  $stepper-error-divider-height: 2rem;
  $stepper-error-divider-color: #ffffff !important;

  .stepper-nav.error {
    background-color: $stepper-error-color;

    .v-stepper__step {
      + .v-divider {
        border-color: $stepper-error-divider-color;
      }

      ::v-deep {
        .v-stepper__step__step {
          color: $stepper-error-color;
          background-color: $stepper-error-font-color;
        }

        .v-stepper__label {
          color: $stepper-error-font-color;
        }
      }

      &:hover,
      &--active,
      &--complete {
        color: $stepper-error-color;
      }
    }

    .v-stepper__step--complete {
      ::v-deep {
        .v-stepper__step__step {

          .v-icon {
            color: $stepper-error-color;
          }
        }
      }
    }
  }

  .loading-container {
    background: rgba(255,255,255, 0.8);
    z-index: 1;
  }

  // Stepper Content
  .stepper-content {
    flex: 1 1 auto;

    &__count {
      text-transform: uppercase;
      font-size: 0.875rem;
      font-weight: bold;
    }
  }

  ::v-deep {
    .step-btns {
      .v-btn {
        min-width: 7rem !important;

        &.primary {
          font-weight: 700;
        }
      }
    }
  }

  .error + hr {
    display: none;
  }
</style>
