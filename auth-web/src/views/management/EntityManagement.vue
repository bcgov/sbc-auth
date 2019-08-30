<template>
  <div>
    <h2>Manage Businesses</h2>
    <v-flex class="text-xs-right">
        <v-btn @click="addBusiness" color="primary" large>
          <span>{{'Add Business'}}</span>
        </v-btn>
    </v-flex>
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
  addBusiness () {
    this.$router.push('/addbusiness')
  }
}
</script>
