<template>
  <div>
    <h2>Manage Businesses</h2>
    <AffiliatedEntityList />
  </div>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import AffiliatedEntityList from '@/components/auth/AffiliatedEntityList.vue'

@Component({
  components: { AffiliatedEntityList }
})
export default class EntityManagement extends Vue {}
</script>
