// You can declare a mixin as the same style as components.
<script lang="ts">
import Component from 'vue-class-component'
import { DataOptions } from 'vuetify'
import Vue from 'vue'

@Component({
})
export default class PaginationMixin extends Vue {
  protected readonly ITEMS_PER_PAGE = 2
  protected readonly PAGINATION_COUNTER_STEP = 4

  DEFAULT_DATA_OPTIONS:DataOptions = {
    page: 1,
    itemsPerPage: this.ITEMS_PER_PAGE,
    sortBy: [],
    sortDesc: [],
    groupBy: [],
    groupDesc: [],
    multiSort: false,
    mustSort: false
  }

  protected get getPaginationOptions () {
    return [...Array(this.PAGINATION_COUNTER_STEP)].map((value, index) => this.ITEMS_PER_PAGE * (index + 1))
  }
}
</script>
