<template>
  <div>
    <h2>Manage Users</h2>
    <v-data-table
      :headers="headers"
      :items="users"
      :items-per-page="5"
      class="elevation-1"
    >
    </v-data-table>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component({})
export default class UserManagement extends Vue {
  headers = [
    {
      text: 'User',
      align: 'left',
      sortable: true,
      value: 'fullname'
    },
    {
      text: 'Roles',
      align: 'left',
      sortable: true,
      value: 'roles'
    },
    {
      text: 'Status',
      align: 'left',
      sortable: true,
      value: 'status'
    }
  ]

  users = []
}
</script>
