<template>
  <section v-if="accountUnderReviewAdmin">
    <h2 class="mb-5">
      {{ `${tabNumber !== null ? `${tabNumber}. ` : ''}${title}` }}
    </h2>

    <v-row>
      <v-col class="cols-12 col-sm-3 py-2">
        Given Name(s)
      </v-col>
      <v-col class="py-2">
        {{ accountUnderReviewAdmin.firstname }} {{ accountUnderReviewAdmin.lastname }}
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 col-sm-3 py-2">
        Username
      </v-col>
      <v-col class="py-2">
        {{ accountUnderReviewAdmin.username }}
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 col-sm-3 py-2">
        Email Address
      </v-col>
      <v-col class="py-2">
        {{ accountUnderReviewAdminContact && accountUnderReviewAdminContact.email }}
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 col-sm-3 py-2">
        Phone Number
      </v-col>
      <v-col class="py-2">
        {{ accountUnderReviewAdminContact && accountUnderReviewAdminContact.phone }}
      </v-col>
    </v-row>
  </section>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { Contact } from '@/models/contact'
import { User } from '@/models/user'

@Component({})
export default class AccountAdministrator extends Vue {
  @Prop({ default: null }) private tabNumber: number
  @Prop({ default: 'Account Administrator' }) private title: string
  @Prop({ default: {} }) accountUnderReviewAdmin: User
  @Prop() accountUnderReviewAdminContact: Contact
}
</script>
