<template>
  <v-card>
    <v-card-title class="card-title">
      <v-icon
        class="pr-5"
        color="link"
        left
      >
        mdi-bank-check
      </v-icon>
      <b>Short Name and Account Linkage</b>
    </v-card-title>

    <v-card-text
      v-if="isLinked"
      class="pa-5 linked-text"
    >
      All payments from {{ shortNameDetails.shortName }} will be applied to:
      <br>
      <b>{{ accountDisplayText }}</b>
    </v-card-text>

    <v-card-text
      v-else
      class="d-flex justify-space-between pa-5 unlinked-text"
    >
      Payment from this short name is not linked with an account yet.
      <v-btn
        id="link-shortname-btn"
        color="primary"
      >
        Link to Account
      </v-btn>
    </v-card-text>
  </v-card>
</template>
<script lang="ts">

import { computed, defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'ShortNameAccountLinkage',
  props: {
    shortNameDetails: {
      type: Object,
      default: () => ({})
    }
  },
  setup (props) {
    const isLinked = computed<boolean>(() => {
      return props.shortNameDetails?.accountId
    })

    const accountDisplayText = computed<string>(() => {
      return `${props.shortNameDetails.accountId} ${props.shortNameDetails.accountName}`
    })

    return {
      isLinked,
      accountDisplayText
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

.card-title {
  background-color: $app-lt-blue;
  justify-content: left;
}

</style>
