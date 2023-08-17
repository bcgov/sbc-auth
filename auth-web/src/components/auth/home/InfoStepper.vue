<template>
  <div>
    <v-container id="step-buttons-container">
      <template v-for="(step, index) in steps">
        <div
          :key="index"
          class="step"
          @click="goTo(step)"
          @keyup.tab="goTo(step)"
        >
          <v-btn
            :id="step.id"
            fab
            outlined
            :ripple="false"
            color="#1A5A96"
            class="step__icon"
            :class="{ 'filled': isCurrentStep(step) }"
          >
            <span class="step-number">{{ step.step }}</span>
          </v-btn>
          <div
            class="step__label"
            :class="{ 'selected': isCurrentStep(step) }"
          >
            {{ step.text }}
          </div>
          <span :class="{ 'arrow-down': isCurrentStep(step) }" />
        </div>
      </template>
    </v-container>
    <!-- Next Step Button -->
    <div class="next-step-wrapper">
      <span
        class="next-step-btn"
        :class="{ 'hide-next-btn': hideBtn }"
        @click="nextStep()"
      >
        <u>Next Step</u><v-icon color="#1A5A96">mdi-menu-right</v-icon>
      </span>
    </div>
  </div>
</template>

<script lang="ts">
// Libraries
import { computed, defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'InfoStepper',
  setup (props, { root }) {
    const steps = [
      {
        id: 'step-1-btn',
        step: 1,
        text: 'Decide on a Business Type',
        to: '/decide-business'
      },
      {
        id: 'step-2-btn',
        step: 2,
        text: 'Request a Name',
        to: '/request-name'
      },
      {
        id: 'step-3-btn',
        step: 3,
        text: 'Register or Incorporate',
        to: '/incorporate-or-register'
      },
      {
        id: 'step-4-btn',
        step: 4,
        text: 'Maintain Your Business',
        to: '/maintain-business'
      }
    ]

    const getCurrentStep = (): number => {
      const route = root.$route?.path
      for (const path of steps) {
        if (path.to === route) {
          return path.step || 0
        }
      }
      return 0
    }

    const hideBtn = computed(() => {
      return getCurrentStep() === steps.length
    })

    const isCurrentStep = (step: { id: string, step: number, text: string, to: string}): boolean => {
      return root.$route?.path === step.to
    }

    const goTo = (step: { id: string, step: number, text: string, to: string}): void => {
      if (!isCurrentStep(step)) root.$router?.push(step.to)
    }

    const nextStep = (): void => {
      const currentStepIndex = getCurrentStep()
      const nextStep = steps[currentStepIndex]
      root.$router?.push(nextStep.to)
    }

    return {
      steps,
      hideBtn,
      isCurrentStep,
      goTo,
      nextStep
    }
  }
})
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  #step-buttons-container {
    display: flex;
  }

  .v-btn:before {
    background-color: $BCgovBG;
  }

  .v-btn--active.no-active::before {
    opacity: 0 !important;
  }

  .filled {
    background-color: $BCgoveBueText1;
    color: $BCgovBG !important;
  }

  .selected {
    color: #212529 !important;
    border-bottom: 3px solid $BCgoveBueText1 !important;
  }

  .step {
    display: flex;
    flex-direction: column;
    flex: 1;
    align-items: center;

    .step-number {
      font-size: 1.5rem;
    }
  }

  .step:hover {
    cursor: pointer;

    .step__icon {
      color: $BCgovBG !important;
      background-color: $BCgoveBueText1;
      opacity: .8;
    }

    .step__label {
      color: $BCgovBlue5;
      opacity: .8;
      text-decoration: underline;
    }
  }

  .step__icon {
    font-size: 1.5rem
  }

  .step__label {
    width: 100%;
    color: $BCgoveBueText1;
    font-weight: bold;
    font-size: 14px;
    margin-top: 10px;
    padding-bottom: 20px !important;
    text-align: center;
    border-bottom: 3px solid #DEE2E6;
    border-bottom-left-radius: 0%;
    border-bottom-right-radius: 0%;
  }

  .arrow-down {
    width: 0;
    height: 0;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-top: 8px solid $BCgoveBueText1;
  }

  .next-step-wrapper {
    position: relative;
    min-height: 24px;
    width: 100%;
    .next-step-btn {
      position: absolute;
      right: 0;
      color: $BCgoveBueText1;
    }

    .next-step-btn:hover {
      cursor: pointer;
      color: $BCgoveBueText2;
    }

    .hide-next-btn {
      display: none;
    }
  }
</style>
