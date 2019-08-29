<template>
  <v-container>
    <div class="view-container">
      <article>
        <h1>Create Account</h1>
        <v-card class="profile-card">
          <v-container>
            <h2>Enter User Profile</h2>
            <UserProfileForm/>
          </v-container>
        </v-card>
      </article>
      <aside>
        <SupportInfoCard/>
      </aside>
    </div>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { Component } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'
import UserProfileForm from '@/components/auth/UserProfileForm.vue'
import SupportInfoCard from '@/components/SupportInfoCard.vue'

@Component({
  components: {
    UserProfileForm,
    SupportInfoCard
  }
})
export default class UserProfile extends Vue {

}
</script>
