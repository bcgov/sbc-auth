<template>
  <v-btn
    large
    color="#003366"
    target="_blank"
    rel="noopener noreferrer"
    class="btn-name-request white--text"
    :class="{'btn-name-request-wide': isWide}"
    :href="nameRequestUrl">
    <span class="btn-text">Request a Name</span>
  </v-btn>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import { LDFlags } from '@/util/constants'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'

@Component({})
export default class NameRequestButton extends Vue {
  @Prop() isWide: boolean

  private get nameRequestUrl (): string {
    return LaunchDarklyService.getFlag(LDFlags.LinkToNewNameRequestApp)
      ? ConfigHelper.getNameRequestUrl()
      : ConfigHelper.getNroUrl()
  }
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
