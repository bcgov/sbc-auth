<template>
  <v-container id="step-buttons-container">
    <template v-for="(step, index) in steps">
      <div class="step" :key="index">
        <v-btn class="step__icon" :id=step.id :outlined="true" fab color="#1A5A96" :to=step.to :disabled=step.disabled>
          <v-icon>{{step.step}}</v-icon>
        </v-btn>
        <v-btn class="step__label" text color="#1A5A96" :to=step.to :disabled=step.disabled>
          {{step.text}}
        </v-btn>
        <div class="arrow-down"></div>
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
      icon: 'mdi-number-1',
      text: 'Decide on a Business Type',
      to: '/decide-business-info'
    },
    {
      id: 'step-2-btn',
      step: 2,
      icon: 'mdi-number-2',
      text: 'Request a Name',
      to: '/request-name-info'
    },
    {
      id: 'step-3-btn',
      step: 3,
      icon: 'mdi-number-3',
      text: 'Incorporate or Register',
      to: '/incorp-or-register-info'
    },
    {
      id: 'step-4-btn',
      step: 4,
      icon: 'mdi-number-4',
      text: 'Maintain Your Business',
      to: '/maintain-business-info'
    }
  ]
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  #step-buttons-container {
    display: flex;
  }

  .step {
    display: flex;
    flex-direction: column;
    flex: 1;
    align-items: center;
    justify-content: center;
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
    border-bottom: 3px solid $BCgoveBueText1;
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
