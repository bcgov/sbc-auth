<template>
  <v-tooltip top max-width="450px" light content-class="contact-us-tooltip" v-model="showTip">
    <template v-slot:activator="{ attrs }">
      <span :attrs="attrs" @click="showTip = !showTip" class="contact-us-tooltip-text">Contact Us</span>
    </template>
    <v-card class="contact-us-tooltip-content">
      <h3 class="mb-3">Don't have a Passcode for your Cooperative Association?</h3>
      <p>If you have not received your Access Letter from BC Registries, or have lost your Passcode, please contact us
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

// This component template is for future implementation.
// Values in the template are static and not to be used until we receive further information.
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

  .contact-us-tooltip {
    background-color: transparent;
    opacity: 1 !important;

    .contact-us-tooltip-content {
      min-width: 30rem;
      padding: 2rem;
      font-size: 0.75rem;
    }
  }

  .contact-us-tooltip-text {
    text-decoration: underline dashed;
  }

  .contact-us-tooltip-text:hover {
    cursor: pointer;
  }
</style>
