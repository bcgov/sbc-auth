<template>
  <v-container id="step-buttons-container">
    <template v-for="(step, index) in steps">
      <div class="step" :key="index">
        <v-btn
          fab
          class="step__icon"
          active-class="no-active filled"
          :id=step.id :outlined="true"
          color="#1A5A96"
          :to=step.to>
          <v-icon>{{step.step}}</v-icon>
        </v-btn>
        <v-btn class="step__label" active-class="no-active selected" text color="#1A5A96" :to=step.to>
          {{step.text}}
        </v-btn>
        <span :class="{ 'arrow-down': isCurrentStep(step) }"></span>
      </div>
    </template>
  </v-container>
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
      to: '/decide-business-info'
    },
    {
      id: 'step-2-btn',
      step: 2,
      text: 'Request a Name',
      to: '/request-name-info'
    },
    {
      id: 'step-3-btn',
      step: 3,
      text: 'Incorporate or Register',
      to: '/incorp-or-register-info'
    },
    {
      id: 'step-4-btn',
      step: 4,
      text: 'Maintain Your Business',
      to: '/maintain-business-info'
    }
  ]

  private isCurrentStep (step: any): boolean {
    return this.$route.path === step.to
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
    color: $grat1B!important;
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
    position: relative;
    z-index: 2;
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
</style>
