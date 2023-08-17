<template>
  <v-tooltip
    top
    max-width="450px"
    light
    content-class="tooltip"
  >
    <template #activator="{ on }">
      <span
        v-if="enableBcCccUlc"
        class="tooltip-text"
        v-on="on"
      >Numbered Company</span>
      <span
        v-else
        class="tooltip-text"
        v-on="on"
      >Numbered Benefit Company</span>
    </template>
    <v-card class="tooltip-content">
      <template v-if="enableBcCccUlc">
        <h3 class="mb-3">
          Numbered Company
        </h3>
        <span>A Company can choose to use as its name the incorporation number of the company followed by “B.C. Ltd.”,
          "B.C. Unlimited Liability Company", or "B.C. Community Contribution Company." The incorporation number is
          assigned by the Business Registry after the Incorporation Application is filed and the company is
          incorporated.</span>
      </template>
      <template v-else>
        <h3 class="mb-3">
          Numbered Benefit Company
        </h3>
        <span>A Benefit Company can choose to use as its name the incorporation number of the company followed by “B.C.
          Ltd.” The incorporation number is assigned by the Business Registry after the Incorporation Application is
          filed and the company is incorporated.</span>
      </template>
    </v-card>
  </v-tooltip>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import { LDFlags } from '@/util/constants'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import Vue from 'vue'

@Component({})
export default class NumberedCompanyTooltip extends Vue {
  get enableBcCccUlc (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.EnableBcCccUlc) || false
  }
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
      font-size: $px-12;
    }
  }

  .tooltip-text {
    text-decoration: underline dotted;
    text-underline-offset: 2px;
  }

  .tooltip-text:hover {
    cursor: pointer;
  }
</style>
