<template>
  <v-container
    id="continuation-applications-review"
    class="pa-0"
  >
    <header class="view-header align-center justify-space-between mt-n1 mb-4">
      <h2 class="view-header__title">
        Continuation Authorization Reviews
      </h2>
    </header>

    <!-- Table Contents -->
    <ContinuationApplicationTable
      :reviewSessionStorageKey="reviewSessionStorageKey"
      :reviewPaginationNumberOfItemsKey="reviewPaginationNumberOfItemsKey"
      :reviewPaginationOptionsKey="reviewPaginationOptionsKey"
    />
  </v-container>
</template>

<script lang="ts">
import ContinuationApplicationTable from './ContinuationApplicationTable.vue'
import { SessionStorageKeys } from '@/util/constants'
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'ContinuationApplications',
  components: {
    ContinuationApplicationTable
  },
  data () {
    return {
      reviewSessionStorageKey: SessionStorageKeys.ReviewSearchFilter,
      reviewPaginationNumberOfItemsKey: SessionStorageKeys.ReviewPaginationNumberOfItems,
      reviewPaginationOptionsKey: SessionStorageKeys.ReviewPaginationOptions
    }
  }
})
</script>
