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
      class="pa-5"
    >
      All payments from {{ state.shortName.shortName }} will be applied to:
      <br>
      <b>{{ state.shortName.accountId }} {{ state.shortName.accountName }}</b>
    </v-card-text>

    <v-card-text
      v-else
      class="d-flex justify-space-between pa-5"
    >
      Payment from this short name is not linked with an account yet.
      <v-btn color="primary">
        Link to Account
      </v-btn>
    </v-card-text>
  </v-card>
</template>
<script lang="ts">

import { computed, defineComponent, reactive, watch } from '@vue/composition-api'

export default defineComponent({
  name: 'ShortNameAccountLinkage',
  components: { },
  props: {
    shortName: {
      type: Object,
      default: () => ({})
    }
  },
  setup (props) {
    const state = reactive({
      shortName: {
        accountId: null,
        accountName: null,
        shortName: null
      }
    })

    function setShortName (shortname) {
      state.shortName = shortname
    }

    const isLinked = computed<boolean>(() => {
      return state.shortName?.accountId
    })

    watch(() => props.shortName, () => setShortName(props.shortName), { deep: true })

    return {
      state,
      isLinked
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
