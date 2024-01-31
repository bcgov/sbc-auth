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
        id="search-tab"
        :class="['tab-item-default', tab === 0 ? 'tab-item-active' : 'tab-item-inactive']"
        :ripple="false"
      >
        <b class="ml-1">Unlinked Payments</b>
      </v-tab>
      <v-tab
        id="documents-tab"
        :class="['tab-item-default', tab === 1 ? 'tab-item-active' : 'tab-item-inactive']"
        :ripple="false"
      >
        <b class="mx-1">Linked Bank Short Names</b>
      </v-tab>
    </v-tabs>

    <v-window v-model="tab">
      <v-window-item class="ma-0">
        <v-card
          class="window-item-card"
          flat
        >
          Unlinked go here
        </v-card>
      </v-window-item>
      <v-window-item>
        <v-card
          class="window-item-card"
          flat
        >
          <ShortNameLinked />
        </v-card>
      </v-window-item>
    </v-window>
  </v-container>
</template>
<script lang="ts">
import { defineComponent, onMounted, ref } from '@vue/composition-api'
import ShortNameLinked from '@/components/pay/ShortNameLinked.vue'

export default defineComponent({
  name: 'ShortNameMappingView',
  components: { ShortNameLinked },
  props: {
  },
  setup () {
    onMounted(async () => {
    })
    const tab = ref(null)
    return {
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
  padding: 30px 30px 30px 30px;
}

// Additional to make it work from business-search.
::v-deep {
  .v-tabs-slider-wrapper {
    display: none !important;
  }

  .v-tabs-bar {
    height: inherit !important;
  }

  .v-tab--active:hover:before{
    opacity: 0 !important;
  }
}
</style>
