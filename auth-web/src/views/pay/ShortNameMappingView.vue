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
        Managing received electronic funds transfers
      </v-col>
    </v-row>

    <v-tabs
      v-model="tab"
      style="height: 65px; margin-top: 20px;"
    >
      <v-tab
        id="unlinked-shortname-tab"
        :class="['tab-item-default', tab === 0 ? 'tab-item-active' : 'tab-item-inactive']"
        :ripple="false"
      >
        <b>Unlinked Payments</b>
      </v-tab>
      <v-tab
        id="linked-shortname-tab"
        :class="['tab-item-default', tab === 1 ? 'tab-item-active' : 'tab-item-inactive']"
        :ripple="false"
      >
        <b>Linked Bank Short Names</b><span class="text-pre-wrap"> ({{ shortnameStateTotal }})</span>
      </v-tab>
    </v-tabs>

    <v-window v-model="tab">
      <v-window-item class="ma-0">
        <v-card
          class="window-item-card"
          flat
        >
          <UnlinkedShortNameTable
            @shortname-state-total="shortnameStateTotal = $event"
          />
        </v-card>
      </v-window-item>
      <v-window-item eager>
        <v-card
          class="window-item-card"
          flat
        >
          <LinkedShortNameTable
            @shortname-state-total="shortnameStateTotal = $event"
          />
        </v-card>
      </v-window-item>
    </v-window>
  </v-container>
</template>
<script lang="ts">
import { defineComponent, ref } from '@vue/composition-api'
import LinkedShortNameTable from '@/components/pay/LinkedShortNameTable.vue'
import UnlinkedShortNameTable from '@/components/pay/UnlinkedShortNameTable.vue'

export default defineComponent({
  name: 'ShortNameMappingView',
  components: { LinkedShortNameTable, UnlinkedShortNameTable },
  setup () {
    const tab = ref(null)
    const shortnameStateTotal = ref(0)

    return {
      tab,
      shortnameStateTotal
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
  padding: 30px 30px 30px 30px;
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

// Additional for tables
::v-deep {
  .base-table__header > tr:first-child > th  {
    padding: 0 0 0 0 !important;
  }
  .base-table__header__filter {
    padding-left: 16px;
    padding-right: 4px;
  }
  .base-table__item-row {
    color: #495057;
    font-weight: bold;
  }
  .base-table__item-cell {
    padding: 16px 0 16px 16px;
    vertical-align: middle;
  }
}
</style>
