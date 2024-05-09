<template>
  <v-container
    id="short-name-mapping-view"
    class="container mt-7"
    fluid
  >
    <v-row no-gutters>
      <v-col>
        <h1>Electronic Funds Transfer Received Payments</h1>
      </v-col>
    </v-row>
    <v-row
      class="mt-1 pt-2"
      justify="start"
      no-gutters
    >
      <v-col
        class="account-label pr-5"
        cols="auto"
      >
        Manage received Electronic Funds Transfers
      </v-col>
    </v-row>

    <v-tabs
      v-model="tab"
      style="height: 65px; margin-top: 44px;"
      @change="onTabChange"
    >
      <v-tab
        id="shortname-summary-tab"
        :class="['tab-item-default', tab === 0 ? 'tab-item-active' : 'tab-item-inactive']"
        :ripple="false"
      >
        <b>All Short Names</b>
        <span class="font-weight-regular">
          &nbsp;({{ state.summaries }})
        </span>
      </v-tab>
      <v-tab
        id="linked-shortname-tab"
        :class="['tab-item-default', tab === 1 ? 'tab-item-active' : 'tab-item-inactive']"
        :ripple="false"
      >
        <b>EFT Enabled Accounts</b><span class="font-weight-regular">
          &nbsp;({{ state.linked }})</span>
      </v-tab>
    </v-tabs>

    <v-window v-model="tab">
      <v-window-item class="ma-0">
        <v-card
          class="window-item-card"
          flat
        >
          <ShortNameSummaryTable
            :linked-account="state.linkedAccount"
            @shortname-state-total="state.summaries = $event"
            @on-link-account="onLinkAccount"
          />
        </v-card>
      </v-window-item>
      <v-window-item eager>
        <v-card
          class="window-item-card"
          flat
        >
          <LinkedShortNameTable
            @shortname-state-total="state.linked = $event"
          />
        </v-card>
      </v-window-item>
    </v-window>
  </v-container>
</template>
<script lang="ts">
import { defineComponent, onMounted, reactive, ref } from '@vue/composition-api'
import ConfigHelper from '@/util/config-helper'
import LinkedShortNameTable from '@/components/pay/LinkedShortNameTable.vue'
import { SessionStorageKeys } from '@/util/constants'
import ShortNameSummaryTable from '@/components/pay/ShortNameSummaryTable.vue'

export default defineComponent({
  name: 'ShortNameMappingView',
  components: { LinkedShortNameTable, ShortNameSummaryTable },
  setup () {
    const tab = ref(null)
    const state = reactive({
      linked: 0,
      summaries: 0,
      linkedAccount: {},
      isMounted: false
    })

    function onLinkAccount (account: any) {
      tab.value = 0
      state.linkedAccount = account
      ConfigHelper.addToSession(SessionStorageKeys.ShortNamesTabIndex, tab.value)
    }

    function onTabChange () {
      if (!state.isMounted) return
      ConfigHelper.addToSession(SessionStorageKeys.ShortNamesTabIndex, tab.value)
    }

    onMounted(() => {
      const linkedAccount = ConfigHelper.getFromSession(SessionStorageKeys.LinkedAccount)
      if (linkedAccount) {
        state.linkedAccount = JSON.parse(linkedAccount)
        ConfigHelper.removeFromSession(SessionStorageKeys.LinkedAccount)
      }
      const shortNamesTabIndex = ConfigHelper.getFromSession(SessionStorageKeys.ShortNamesTabIndex)
      tab.value = shortNamesTabIndex ? parseInt(shortNamesTabIndex) : 0
      state.isMounted = true
    })

    return {
      onLinkAccount,
      state,
      onTabChange,
      tab
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
.tab-item-inactive {
  color: white !important;
  background-color: $BCgovBlue5;
  box-shadow: inset 0 0 5px 1px $gray9;
  margin-top: 5px;
  transition: none !important;
}

.tab-item-inactive:hover {
  background-color: $BCgovBlue5 !important;
  box-shadow: none !important;
}

.tab-item-active {
  color: $gray8 !important;
  background-color: white;
  transition: none !important;
}

.tab-item-default {
  border-radius: 5px 5px 0 0 !important;
  height: 67px;
  width: 50%;
  min-width: 50%;
  font-size: 1.125rem;
}

.window-item-card {
  padding: 40px 30px 40px 30px;
}

.text-pre-wrap {
  white-space: pre-wrap !important;
}

// Additional to make it work from business-search.
::v-deep {
  .v-tabs-slider-wrapper {
    display: none !important;
  }

  .v-tabs-bar {
    height: inherit !important;
    background-color: transparent !important;
  }

  .v-tab--active:hover:before{
    opacity: 0 !important;
  }
}

.account-linking-dialog ::v-deep .v-card__actions {
  display: flex;
  background: red!important;
}

</style>
