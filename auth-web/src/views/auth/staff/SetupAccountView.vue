<template>
  <v-container>
    <div class="view-container">
      <article>
        <h1 class="mb-5">Setup Account</h1>
        <v-card class="profile-card">
          <v-container>
            <v-card-text>
              <SetupAccountForm />
            </v-card-text>
          </v-container>
        </v-card>
      </article>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import SetupAccountForm from '@/components/auth/staff/SetupAccountForm.vue'

@Component({
  components: {
    SetupAccountForm
  }
})
export default class SetupAccountView extends Vue { }
</script>

<style lang="scss" scoped>
  article {
    flex: 1 1 auto;
    margin: 0 auto;
    max-width: 50rem;
  }
</style>
