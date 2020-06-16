<template>
  <v-tooltip top max-width="450px" light content-class="tooltip" v-model="showTip">
    <template v-slot:activator="{ attrs }">
      <span :attrs="attrs" @click="showTip = !showTip" class="tooltip-text">Contact Us</span>
    </template>
    <v-card class="tooltip-content">
      <h3 class="mb-3">Don't have a Passcode for your Cooperative Association?</h3>
      <p>If you have no received your Access Letter from BC Registries, or have lost your Passcode, please contact us
        at:</p>
      <section>
        <p class="mb-0">Toll Free: 1-877-526-1526</p>
        <p class="mb-0">Phone: 250-387-7848</p>
        <p>Email: bcregistries@gov.bc.ca</p>
      </section>
      <v-spacer></v-spacer>
      <section>
        <p class="mb-0">Hours of Operation:</p>
        <p>Monday to Friday, 8:30am - 4:30pm PST</p>
      </section>
      <a href="">Frequently Asked Questions</a>
    </v-card>
  </v-tooltip>
</template>

<script lang="ts">
import { Component, Prop } from 'vue-property-decorator'
import Vue from 'vue'

@Component({})
export default class ContactUsTooltip extends Vue {
  private showTip = false
}
</script>
<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  a:hover {
    color: $BCgoveBueText2;
  }

  .tooltip {
    background-color: transparent;
    opacity: 1 !important;

    .tooltip-content {
      min-width: 30rem;
      padding: 2rem;
      font-size: 0.75rem;
    }
  }

  .tooltip-text {
    text-decoration: underline dashed;
  }

  .tooltip-text:hover {
    cursor: pointer;
  }
</style>
