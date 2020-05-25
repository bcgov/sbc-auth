<template>
  <v-tooltip top max-width="450px" light content-class="tooltip">
    <template v-slot:activator="{ on }">
      <span v-on="on" class="tooltip-text"><u>numbered Benefit Company</u></span>
    </template>
    <v-card class="tooltip-content">
      <h3 class="mb-3">Numbered Benefit Company</h3>
      <span>Lorem ipsum... some definition of a numbered benefit company would go into this slot here</span>
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

    .tooltip-content {
      padding: 2rem;
    }
  }

  .tooltip-text {
    color: $BCgoveBueText1;
  }

  .tooltip-text:hover {
    color: $BCgoveBueText2;
    cursor: pointer;
  }
</style>
