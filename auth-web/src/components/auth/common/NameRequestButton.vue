<template>
  <v-btn
    large
    color="#003366"
    target="_blank"
    rel="noopener noreferrer"
    class="btn-name-request white--text"
    :class="{'btn-name-request-wide': isWide}"
    :href="nroUrl">
    <span class="btn-text">Request a Name</span>
  </v-btn>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'

@Component({})
export default class NameRequestButton extends Vue {
  private nroUrl = ConfigHelper.getNroUrl()
  @Prop() isWide: boolean
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  .btn-name-request {
    font-weight: bold;
    min-height: 2.75rem;
    width: 10rem;
    background-color: $BCgovBlue5;
  }

  .btn-name-request-wide {
    width: 100%;
    margin-bottom: 0.8125rem;
  }
</style>
