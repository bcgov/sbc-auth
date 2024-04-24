<template>
  <v-card v-if="shortNameDetails.shortName">
    <ShortNameLinkingDialog
      :isShortNameLinkingDialogOpen="isShortNameLinkingDialogOpen"
      :selectedShortName="shortNameDetails"
      @close-short-name-linking-dialog="closeShortNameLinkingDialog"
      @on-link-account="onLinkAccount"
    />
    <v-card-title class="card-title">
      <v-icon
        class="pr-5"
        color="link"
        left
      >
        mdi-bank-transfer
      </v-icon>
      Short Name and Account Linkage
    </v-card-title>

    <v-card-text
      v-if="isLinked"
      class="pa-5 linked-text"
    >
      <v-btn
        id="link-shortname-btn"
        color="primary"
        outlined
        dark
        large
        class="mt-0 mr-4 font-weight-regular"
        @click="openAccountLinkingDialog()"
      >
        + Link a New Account
      </v-btn>
      <div>
        All payments from {{ shortNameDetails.shortName }} will be applied to: <b>{{ accountDisplayText }}</b>
      </div>
    </v-card-text>

    <v-card-text
      v-else
      class="d-flex justify-space-between pa-5 unlinked-text"
    >
      Payment from this short name is not linked with an account yet.
      <v-btn
        id="link-shortname-btn"
        color="primary"
        @click="openAccountLinkingDialog()"
      >
        Link to Account
      </v-btn>
    </v-card-text>
  </v-card>
</template>
<script lang="ts">

import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import ConfigHelper from '@/util/config-helper'
import { SessionStorageKeys } from '@/util/constants'
import ShortNameLinkingDialog from '@/components/pay/eft/ShortNameLinkingDialog.vue'

export default defineComponent({
  name: 'ShortNameAccountLinkage',
  components: { ShortNameLinkingDialog },
  props: {
    shortNameDetails: {
      type: Object,
      default: () => ({})
    }
  },
  setup (props, { root }) {
    const state = reactive({
      isShortNameLinkingDialogOpen: false
    })

    const isLinked = computed<boolean>(() => {
      return props.shortNameDetails?.accountId
    })

    const accountDisplayText = computed<string>(() => {
      return `${props.shortNameDetails.accountId} ${props.shortNameDetails.accountName}`
    })

    function openAccountLinkingDialog () {
      state.isShortNameLinkingDialogOpen = true
    }

    function closeShortNameLinkingDialog () {
      state.isShortNameLinkingDialogOpen = false
    }

    function onLinkAccount (account: any) {
      ConfigHelper.addToSession(SessionStorageKeys.LinkedAccount, JSON.stringify(account))
      ConfigHelper.addToSession(SessionStorageKeys.ShortNamesTabIndex, 1)
      root.$router.push('/pay/manage-shortnames')
    }

    return {
      ...toRefs(state),
      isLinked,
      accountDisplayText,
      openAccountLinkingDialog,
      closeShortNameLinkingDialog,
      onLinkAccount
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

.card-title {
  background-color: $app-lt-blue;
  justify-content: left;
  height: 75px;
  font-weight: bold;
  font-size: 1.125rem;

  .v-icon {
    font-size: 36px;
  }
}

</style>
