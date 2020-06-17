<template>
  <v-tooltip top max-width="450px" light content-class="tooltip">
    <template v-slot:activator="{ on }">
      <span v-on="on" class="tooltip-text">Numbered Benefit Company</span>
    </template>
    <v-card class="tooltip-content">
      <h3 class="mb-3">Numbered Benefit Company</h3>
      <span>A Benefit Company can choose to use as its name the incorporation number of the company followed by “B.C.
        Ltd.” The incorporation number is assigned by the Business Registry after the Incorporation Application is filed
        and the company is incorporated.</span>
    </v-card>
  </v-tooltip>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import Vue from 'vue'

@Component({})
export default class NumberedCompanyTooltip extends Vue {
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
