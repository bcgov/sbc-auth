<template>
  <div>
    <v-container id="step-buttons-container">
      <template v-for="(step, index) in steps">
        <div class="step" :key="index">
          <v-btn
            fab
            outlined
            class="step__icon"
            active-class="filled no-active"
            :id=step.id
            color="#1A5A96"
            :to=step.to>
            <v-icon>{{step.step}}</v-icon>
          </v-btn>
          <v-btn class="step__label" active-class="selected no-active" text color="#1A5A96" :to=step.to>
            {{step.text}}
          </v-btn>
          <span :class="{ 'arrow-down': isCurrentStep(step) }"></span>
        </div>
      </template>
    </v-container>
    <div class="next-step-wrapper">
      <span class="next-step-btn" :class="{ 'hide-next-btn': getCurrentStep() === steps.length }" @click="nextStep()">
        <u>Next Step</u><v-icon color="#1A5A96">mdi-menu-right</v-icon>
      </span>
    </div>
  </div>
</template>

<script lang="ts">
// Libraries
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class Stepper extends Vue {
  private steps: Array<any> = [
    {
      id: 'step-1-btn',
      step: 1,
      text: 'Decide on a Business Type',
      to: '/home/decide-business'
    },
    {
      id: 'step-2-btn',
      step: 2,
      text: 'Request a Name',
      to: '/home/request-name'
    },
    {
      id: 'step-3-btn',
      step: 3,
      text: 'Incorporate or Register',
      to: '/home/incorporate-or-register'
    },
    {
      id: 'step-4-btn',
      step: 4,
      text: 'Maintain Your Business',
      to: '/home/maintain-business'
    }
  ]

  private nextStep (): void {
    const currentStepIndex = this.getCurrentStep()
    const nextStep = this.steps[currentStepIndex]
    this.$router.push(nextStep.to)
  }

  private isCurrentStep (step: any): boolean {
    return this.$route.path === step.to
  }

  private getCurrentStep (): number {
    const route = this.$route.path
    for (const path of this.steps) {
      if (path.to === route) {
        return path.step || 0
      }
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  #step-buttons-container {
    display: flex;
  }

  .v-btn--active.no-active::before {
    opacity: 0 !important;
  }

  .filled {
    background-color: $BCgoveBueText1!important;
    color: $BCgovBG!important;
  }

  .selected {
    color: #212529!important;
    border-bottom: 3px solid $BCgoveBueText1!important;
  }

  .step {
    display: flex;
    flex-direction: column;
    flex: 1;
    align-items: center;
  }

  .step__icon {
    margin-bottom: .5rem;
    position: relative;
    font-weight: 400;
  }

  .step__label {
    width: 100%;
    font-weight: bold;
    font-size: 14px;
    margin-top: 10px;
    padding-bottom: 20px!important;
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
