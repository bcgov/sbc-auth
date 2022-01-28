<template>
  <v-btn
    large
    color="#003366"
    class="btn-name-request white--text"
    :class="{'btn-name-request-wide': isWide}"
    @click="goToNameRequest()"
  >
    <span class="btn-text">Request a Name</span>
  </v-btn>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import { LDFlags } from '@/util/constants'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'

@Component({})
export default class NameRequestButton extends Vue {
  @Prop() isWide: boolean

  // open Name Request in current tab to retain current account and user
  goToNameRequest (): void {
    if (LaunchDarklyService.getFlag(LDFlags.LinkToNewNameRequestApp)) {
      window.location.href = appendAccountId(ConfigHelper.getNameRequestUrl())
    } else {
      window.location.href = appendAccountId(ConfigHelper.getNroUrl())
    }
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
