<template>
  <div>
    <h2>Manage Businesses</h2>
    <AffiliatedEntityList @add-business="showAddBusinessModal()"/>
  </div>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import AffiliatedEntityList from '@/components/auth/AffiliatedEntityList.vue'

@Component({
  components: { AffiliatedEntityList }
})
export default class EntityManagement extends Vue {
  showAddBusinessModal () {
    // Todo: Show the add business popup once it is merged.
  }
}
</script>
