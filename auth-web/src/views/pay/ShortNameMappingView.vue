<template>
  <v-container
    id="dashboard"
    class="container mt-4"
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
    >
      <v-tab
        id="unlinked-shortname-tab"
        :class="['tab-item-default', tab === 0 ? 'tab-item-active' : 'tab-item-inactive']"
        :ripple="false"
      >
        <b>Unlinked Payments</b>
        <span class="font-weight-regular">
          &nbsp;({{ state.unlinked }})
        </span>
      </v-tab>
      <v-tab
        id="linked-shortname-tab"
        :class="['tab-item-default', tab === 1 ? 'tab-item-active' : 'tab-item-inactive']"
        :ripple="false"
      >
        <b>Linked Bank Short Names</b><span class="font-weight-regular">
          &nbsp;({{ state.linked }})</span>
      </v-tab>
    </v-tabs>

    <v-window v-model="tab">
      <v-window-item class="ma-0">
        <v-card
          class="window-item-card"
          flat
        >
          <UnlinkedShortNameTable
            @shortname-state-total="state.unlinked = $event"
            @link-account="linkAccount"
          />
        </v-card>
      </v-window-item>
      <v-window-item eager>
        <v-card
          class="window-item-card"
          flat
        >
          <LinkedShortNameTable
            :linked-account="state.linkedAccount"
            @shortname-state-total="state.linked = $event"
          />
        </v-card>
      </v-window-item>
    </v-window>
  </v-container>
</template>
<script lang="ts">
import { defineComponent, reactive, ref } from '@vue/composition-api'
import LinkedShortNameTable from '@/components/pay/LinkedShortNameTable.vue'
import UnlinkedShortNameTable from '@/components/pay/UnlinkedShortNameTable.vue'

export default defineComponent({
  name: 'ShortNameMappingView',
  components: { LinkedShortNameTable, UnlinkedShortNameTable },
  setup () {
    const tab = ref(null)
    const state = reactive({
      linked: 0,
      unlinked: 0,
      linkedAccount: {}
    })

    function linkAccount (account: any) {
      tab.value = 1
      state.linkedAccount = account
    }

    return {
      tab,
      state,
      linkAccount
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
