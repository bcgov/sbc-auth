<template>
  <v-container class="view-container">
       <v-row justify="center">
      <v-col cols="12" sm="6" class="text-center">
        <v-icon size="40" color="error" class="mb-6">mdi-lock-outline</v-icon>
        <h1>Account Suspended</h1>
        <div v-if="isAdmin">
             <p class="mt-8 mb-10">Your account is suspended. For more information, please contact the BC Online Partnership Office at:<br/></p>
             <p class="mt-1 mb-1">Email: <span class="text-underline">bconline@gov.bc.ca</span></p>
             <p>Telephone: 1-800-663-6102</p>
        </div>
        <div v-else>
        <p class="mt-8 mb-10">Your account is suspended. Please contact the account administrator</p>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Prop, Vue } from 'vue-property-decorator'

export default class AccountSuspendedView extends Vue {
  @Prop({ default: false }) isAdmin: Boolean
}
</script>
<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.text-underline {
    text-decoration: underline;
}
</style>
